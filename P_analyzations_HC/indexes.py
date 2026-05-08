#from osgeo import gdal
from datacube import Datacube
#import sys
from get_dataset import check_data
#for wofs
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask
import numpy as np
import rasterio
from set_AWS import set_AWS
from dask.distributed import Client, LocalCluster

class env_ind:
    def __init__(self):
        self.dc = Datacube(app='Hellas_Cube')
        self.check=check_data(self.dc)

    def ndvi(self,place, date1, date2):
        desired_collections = ["sentinel_2_l2a"]
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets, 
            geopolygon=odc_geom,             
            time=desired_dates,
            output_crs="EPSG:32635",     
            resolution=(-10, 10),
            measurements=["red", "nir"],
            dask_chunks={"time": 1, "x": "auto", "y": "auto"}
        )
        #NDVI INDEX
        red=ds["red"].astype("float32")
        nir=ds["nir"].astype("float32")  
        ndvi_index = (nir - red) / (nir + red)
        ndvi_index = ndvi_index.isel(time=0).compute()
        result={
            "mean":round(float(ndvi_index.mean().values), 3),
            "min":round(float(ndvi_index.min().values), 3),
            "max":round(float(ndvi_index.max().values), 3),
            "std":round(float(ndvi_index.std().values), 3)
        }
        return result

    #NDCI INDEX
    def ndci(self,place,date1,date2):
        desired_collections = ["sentinel_2_l2a"]
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets,  
            geopolygon=odc_geom,             
            time=desired_dates,
            output_crs="EPSG:32635",     
            resolution=(-10, 10),
            measurements=["red", "rededge1"],
            dask_chunks={"time": 1, "x": "auto", "y": "auto"}          
        )
        red=ds["red"].astype("float32")
        rededg1=ds["rededge1"].astype("float32")  
        ndci_index = (rededg1 - red) / (rededg1 + red)
        ndci_index = ndci_index.isel(time=0).compute()
        result={
            "mean":round(float(ndci_index.mean().values), 3),
            "min":round(float(ndci_index.min().values), 3),
            "max":round(float(ndci_index.max().values), 3),
            "std":round(float(ndci_index.std().values), 3)
        }
        return result

    #NDTI
    def ndti(self, place,date1,date2):
        desired_collections = ["sentinel_2_l2a"]
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets,
            geopolygon=odc_geom,     
            time=desired_dates,
            output_crs="EPSG:32635",
            resolution=(-10, 10),
            measurements=["red", "green"],
            dask_chunks={"time": 1, "x": "auto", "y": "auto"}
        )
        red=ds["red"].astype("float32")
        green=ds["green"].astype("float32")
        ndti_index = (red - green) / (red + green)
        ndti_index = ndti_index.isel(time=0).compute()
        result={
            "mean":round(float(ndti_index.mean().values), 3),
            "min":round(float(ndti_index.min().values), 3),
            "max":round(float(ndti_index.max().values), 3),
            "std":round(float(ndti_index.std().values), 3)
        }
        return result

    #WOFS ALGORYTHM
    def flood_wofs(self,place, date1, date2):
        desired_collections = ["ls8_c2l2_sr"]
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections)
        set_AWS()
        with rasterio.Env():
            ds = self.dc.load(
                product=desired_collections,
                datasets=datasets,  
                geopolygon=odc_geom,             
                time=desired_dates,
                output_crs="EPSG:32635",     
                resolution=(-30, 30),
                measurements=["red", "green", "blue", "nir08", "swir16", "swir22", "qa_pixel"],
                dask_chunks={"time": 1, "x": "auto", "y": "auto"}
            )
        ds= ds.compute()
        cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8",cover_types=['clear', 'water'], collection='c2', level='l2')
        sr_bands = ['red', 'green', 'blue', 'nir08', 'swir16', 'swir22']
        nodata_mask = (ds[sr_bands] != 0).to_array(dim='band').all(dim='band')
        for band in sr_bands:
            ds[band] = ((ds[band] * 0.0000275 - 0.2) * 10000).clip(0, 10000).astype(np.int16)
        combined_mask = cloud_mask & nodata_mask
        
        water_classification = wofs_classify(ds, x_coord="x", y_coord="y", clean_mask=combined_mask, no_data=255)
        scenes = []
        for i in range(len(water_classification.time)):
            scene = water_classification.wofs.isel(time=i)
            date  = str(water_classification.time.isel(time=i).values)[:10] #getting scenes that are valid scenes
            clear_water     = int((scene == 1).sum().item())
            clear_not_water = int((scene == 0).sum().item())
            no_data         = int((scene == 255).sum().item())
            total_clear     = clear_water + clear_not_water  

            if total_clear < 100:
                scenes.append({"date": date, "status": "too_cloudy", "water_pct": None})    #When the geotiff are too cloudy!
                continue

            water_pct = round((clear_water / total_clear) * 100, 1)
            scenes.append({
                "date":      date,
                "water_pct": water_pct,
                "status":    "dry" if water_pct < 25 else "healthy"
            })
            valid_observations = (water_classification.wofs != 255).sum(dim="time")
            water_observations = (water_classification.wofs == 1).sum(dim="time")
            reliable_pixels    = valid_observations >= max(1, len(water_classification.time) // 3) #dynamic minimum valid observzations
            water_frequency    = (water_observations / valid_observations.where(valid_observations > 0)) * 100
            water_frequency    = water_frequency.where(reliable_pixels)
            valid_scenes = [s for s in scenes if s["status"] != "too_cloudy"]
            dry_scenes   = [s for s in valid_scenes if s["status"] == "dry"]

            return {
                "scenes": scenes,
                "permanent_water":  f"{(water_frequency == 100).mean().item() * 100:.2f}%",
                "persistent_water": f"{(water_frequency > 80).mean().item() * 100:.2f}%",
                "seasonal_water":   f"{(water_frequency > 50).mean().item() * 100:.2f}%",
                "occasional_water": f"{(water_frequency > 0).mean().item() * 100:.2f}%",
                "conclusion":    "dried" if dry_scenes else "healthy",
                "total_scenes":  len(scenes),
                "valid_scenes":  len(valid_scenes),
                "cloudy_scenes": len(scenes) - len(valid_scenes),
                "confidence":    "low" if len(valid_scenes) < 3 else "high"
            }
    
    #WATER CLARITY ALGORYTHM
    def sdd(self, place, date1, date2):
        desired_collections = ["sentinel_2_l2a"]
        odc_geom, desired_dates, datasets = self.check.checking(place, date1, date2, desired_collections)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets,
            geopolygon=odc_geom,
            time=desired_dates,
            output_crs="EPSG:32635",
            resolution=(-10, 10),
            measurements=["blue", "green", "red"],
            dask_chunks={"time": 1, "x": "auto", "y": "auto"}
        )
        blue = ds["blue"].astype("float32") * 0.0001
        green = ds["green"].astype("float32") * 0.0001
        red = ds["red"].astype("float32") * 0.0001
        blue = blue.where((blue > 0) & (blue < 1))
        green = green.where((green > 0) & (green < 1))
        red = red.where((red > 0) & (red < 1))
        sdd_map = 10 ** (0.69 + 1.35 * np.log10(blue / red))
        sdd_map = sdd_map.where((sdd_map > 0.1) & (sdd_map < 30))
        sdd_slice = sdd_map.isel(time=0).compute()
        mean_val   = float(sdd_slice.mean().values)
        min_val    = float(sdd_slice.min().values)
        max_val    = float(sdd_slice.max().values)
        std_val    = float(sdd_slice.std().values)
        median_val = float(sdd_slice.median().values)
        p25_val    = float(sdd_slice.quantile(0.25).values)
        p75_val    = float(sdd_slice.quantile(0.75).values)
        def classify(val):
            if val < 1.0:   return "very_turbid"
            if val < 2.5:   return "turbid"
            if val < 5.0:   return "moderate"
            if val < 10.0:  return "clear"
            return "very_clear"

        return {
            "mean_sdd_meters":   round(mean_val, 3),
            "min_sdd_meters":    round(min_val, 3),
            "max_sdd_meters":    round(max_val, 3),
            "std_sdd_meters":    round(std_val, 3),
            "median_sdd_meters": round(median_val, 3),
            "p25_sdd_meters":    round(p25_val, 3),
            "p75_sdd_meters":    round(p75_val, 3),
            "clarity":           classify(mean_val)
        }