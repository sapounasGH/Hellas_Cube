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
#import time

class env_ind:
    def __init__(self):
        self.dc = Datacube(app='Hellas_Cube')
        self.check=check_data(self.dc)
    
    #NDVI(NORMALIZED DIFFRENCE VEGETATION INDEX)
    def ndvi(self,place, date1, date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "nir", "red", client, ["sentinel_2_l2a"])
        return result

    #NDCI(NORMALIZED DIFFRENCE CHLOROFYL INDEX)
    def ndci(self,place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "rededge1", "red", client, ["sentinel_2_l2a"])
        return result

    #NDTI(NORMALIZED DIFFRENCE TURBIDITY INDEX)
    def ndti(self, place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "red", "green", client, ["sentinel_2_l2a"])
        return result
    
    #NDWI(NORMALIZED DIFFRENCE WATER INDEX)
    def ndwi(self, place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "green", "nir", client, ["sentinel_2_l2a"])
        return result

    #NDMI(NORMALIZED DIFFRENCE MOISTURE INDEX)
    def ndmi(self, place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "nir", "swir16", client, ["sentinel_2_l2a"])
        #percentage of the area tha is cover by water
        result["water_extent"] = f"{float((result['mean'] > 0) * 100):.2f}%"
        return result
    
    #NDBI(NORMALIZED DIFFRENCE Built-up INDEX)
    def ndbi(self, place,date1,date2, client):
        #NDBI WORKS BETTER FOR LANDSAT, MAKE CHANGES FOR BETTER RESUTLS, maybe a fix is the nir08 because our product for the ls8 the name of the band is name:nir08
        result=self.normalized_diffrence_index(place, date1, date2, "swir16", "nir", client, ["ls8_c2l2_sr"])
        return result
    
    #NDSI(NORMALIZED DIFFRENCE SNOW INDEX)
    def ndsi(self, place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "green", "swir16", client, ["sentinel_2_l2a"])
        return result

    #NBR (Normalized Burn Ratio)
    def nbr(self, place,date1,date2, client):
        result=self.normalized_diffrence_index(place, date1, date2, "nir", "swir22", client, ["sentinel_2_l2a"])
        return result

    def normalized_diffrence_index(self, place, date1, date2, color1, color2, client, desired_collections):
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets,
            geopolygon=odc_geom,     
            time=desired_dates,
            output_crs="EPSG:32635",
            resolution=(-10, 10),
            measurements=[color1, color2],
            dask_chunks={"time": 1, "x": 1024, "y": 1024}
        )
        color1=ds[color1].astype("float32")
        color1=color1.where(color1>0)
        color2=ds[color2].astype("float32")
        color2=color2.where(color2>0)
        ndi_index = (color1 - color2) / (color1+color2)
        ndi_index = client.compute(ndi_index.median(dim="time"), sync= True)
        result={
            "mean":round(float(ndi_index.mean().values), 3),
            "min":round(float(ndi_index.min().values), 3),
            "max":round(float(ndi_index.max().values), 3),
            "std":round(float(ndi_index.std().values), 3)
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
            #no_data         = int((scene == 255).sum().item())
            total_clear     = clear_water + clear_not_water  
            if total_clear < 100:
                scenes.append({"date": date, "status": "too_cloudy", "water_pct": None})    #When the geotiff are too cloudy
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