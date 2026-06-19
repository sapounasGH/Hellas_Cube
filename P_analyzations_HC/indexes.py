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

#on the SCL scale
"""
SCENE CLASSIFICATION TABLE
| Label | Classification            |
| 0     | NO_DATA                   |
| 1     | SATURATED_OR_DEFECTIVE    |
| 2     | DARK_AREA_PIXELS          |
| 3     | CLOUD_SHADOWS             |
| 4     | VEGETATION                |
| 5     | NOT_VEGETATED             |
| 6     | WATER                     |
| 7     | UNCLASSIFIED              |
| 8     | CLOUD_MEDIUM_PROBABILITY  |
| 9     | CLOUD_HIGH_PROBABILITY    |
| 10    | THIN_CIRRUS               |
| 11    | SNOW                      |

the main idea is that the masking is going to happen using the scl, SCENE CLASSIFICATION
and the masking is 
"""
S2_SCALE = 0.0001

#Functions

#masking the dataset
#for every index we are 
def find_water_scl_mask(ds):
    return ds["scl"].isin([4,5,6,7])

def burn_scl_mask(ds):
    return ds["scl"].isin([2,4,5,7])

def vegetation_moist_build_scl_mask(ds):
    return ds["scl"].isin([4,5,7])

def only_snow_scl_mask(ds):
    return ds["scl"].isin([5,7,11])

def water_inside_scl_mask(ds):
    return ds["scl"].isin([6,7])

def strict_scl_mask(ds):
    return ds["scl"].isin([4,5,6,7,11])

def medium_scl_mask(ds):
    return ds["scl"].isin([2,4,5,6,7,11])

def low_scl_mask(ds):
    return ds["scl"].isin([])
 
 
def stats(da, index_name: str = "") -> dict:
    #returning 
    valid_px=int(da.notnull().sum().values)
    total_px=int(da.size)
    coverage=round((valid_px / total_px) * 100, 2) if total_px > 0 else 0.0
    if valid_px==0:
        return {
            "index":        index_name,
            "error":        "no_valid_pixels",
            "valid_px":     valid_px,
            "total_px":     total_px,
            "coverage_pct": 0.0,
        }
    
    return {
        "index":        index_name,
        "mean":         round(float(da.mean(skipna=True).values),3),
        "median":       round(float(da.median(skipna=True).values),3),
        "min":          round(float(da.min(skipna=True).values),3),
        "max":          round(float(da.max(skipna=True).values),3),
        "std":          round(float(da.std(skipna=True).values),3),
        "p10":          round(float(da.quantile(0.10, skipna=True).values),3),
        "p25":          round(float(da.quantile(0.25, skipna=True).values),3),
        "p75":          round(float(da.quantile(0.75, skipna=True).values),3),
        "p90":          round(float(da.quantile(0.90, skipna=True).values),3),
        "valid_px":     valid_px,
        "total_px":     total_px,
        "coverage_pct": f"{coverage} %"
    }
 
def prefix_stats(d: dict, prefix: str) -> dict:
    return {f"{prefix}_{k}": v for k, v in d.items()}

def load_s2(dc, check, place, date1, date2, req_type, measurements,resolution, product):
    #loading the dataset need to do something diffrent for the resolution
    odc_geom, desired_dates, datasets = check.checking(place, date1, date2, ["sentinel_2_l2a"], req_type)   
    meas=list(dict.fromkeys(measurements + ["scl"]))  #adding scl, SCL is a way to mask the pixels
    ds=dc.load(
        product=product,
        datasets=datasets,
        geopolygon=odc_geom,
        time=desired_dates,
        output_crs="EPSG:32635",
        resolution=resolution,
        measurements=meas,
        dask_chunks={"time": 1, "x": 1024, "y": 1024},
        group_by="solar_day",
    )
    return ds

class env_ind:
    def __init__(self):
        self.dc = Datacube(app='Hellas_Cube')
        self.check=check_data(self.dc)

    #SENTINEL-2
    #NDVI(NORMALIZED DIFFRENCE VEGETATION INDEX)
    def ndvi(self,place, date1, date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "nir", "red", client, ["sentinel_2_l2a"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["nir", "red"], (-10, 10), ["sentinel_2_l2a"])
        mask=strict_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        nir=(ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        red=(ds["red"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((nir - red) / (nir + red)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDVI")
        return result

    #NDCI(NORMALIZED DIFFRENCE CHLOROFYL INDEX)
    def ndci(self,place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "rededge1", "red", client, ["sentinel_2_l2a"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["rededge1", "red"], (-10, 10), ["sentinel_2_l2a"])
        mask=water_inside_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        rededge1=(ds["rededge1"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        red=(ds["red"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((rededge1 - red) / (rededge1 + red)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDCI")
        return result

    #NDTI(NORMALIZED DIFFRENCE TURBIDITY INDEX)
    def ndti(self, place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "red", "green", client, ["sentinel_2_l2a"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["red", "green"], (-10, 10), ["sentinel_2_l2a"])
        mask = water_inside_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        red = (ds["red"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        green = (ds["green"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((red - green) / (red + green)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDTI")
        return result
    
    #NDWI(NORMALIZED DIFFRENCE WATER INDEX) CHANGE IT AND CALCULATE BOTH NDWI (McFeeters) and NDWI (Gao style)
    def ndwi(self, place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "green", "nir", client, ["sentinel_2_l2a"], req_type)
        #NDWI (McFeeters)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["green", "nir"], (-10, 10), ["sentinel_2_l2a"])
        mask = water_inside_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        green = (ds["green"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        nir = (ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((green - nir) / (green + nir)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result1=stats(median, "NDWI (McFeeters)")
        #NDWI (Gao style)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["nir", "swir16"], (-20, 20), ["sentinel_2_l2a"])
        mask = water_inside_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        nir = (ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds["swir16"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((nir - swir16) / (nir + swir16)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result2=stats(median, "NDWI (Gao style)")
        return {
            **prefix_stats(result1, "mcf"),
            **prefix_stats(result2, "gao"),
        }

    #NDMI(NORMALIZED DIFFRENCE MOISTURE INDEX)
    def ndmi(self, place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "nir", "swir16", client, ["sentinel_2_l2a"], req_type)
        #percentage of the area tha is cover by water
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["nir", "swir16"], (-20, 20), ["sentinel_2_l2a"])
        mask = vegetation_moist_build_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        nir = (ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds["swir16"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((nir - swir16) / (nir + swir16)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDMI")
        result["water_extent"] = f"{float((result['mean'] > 0) * 100):.2f}%"
        return result
    
    #NDBI(NORMALIZED DIFFRENCE Built-up INDEX)
    def ndbi(self, place,date1,date2, client, req_type):
        #NDBI WORKS BETTER FOR LANDSAT, MAKE CHANGES FOR BETTER RESUTLS, maybe a fix is the nir08 because our product for the ls8 the name of the band is name:nir08
        #result=self.normalized_diffrence_index(place, date1, date2, "swir16", "nir", client, ["ls8_c2l2_sr"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["swir16", "nir"], (-20, 20), ["sentinel_2_l2a"])
        mask = vegetation_moist_build_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        swir16 = (ds["swir16"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        nir = (ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((swir16 - nir) / (swir16 + nir)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDBI")
        return result
    
    #NDSI(NORMALIZED DIFFRENCE SNOW INDEX)
    def ndsi(self, place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "green", "swir16", client, ["sentinel_2_l2a"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["green", "swir16"], (-10, 10), ["sentinel_2_l2a"])
        mask = only_snow_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        green = (ds["green"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds["swir16"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((green - swir16) / (green + swir16)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NDSI")
        return result

    #NBR (Normalized Burn Ratio)
    def nbr(self, place,date1,date2, client, req_type):
        #result=self.normalized_diffrence_index(place, date1, date2, "nir", "swir22", client, ["sentinel_2_l2a"], req_type)
        ds=load_s2(self.dc, self.check, place, date1, date2, req_type, ["nir", "swir22"], (-10, 10), ["sentinel_2_l2a"])
        mask = burn_scl_mask(ds)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        nir = (ds["nir"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        swir22 = (ds["swir22"].astype("float32") * S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((nir - swir22) / (nir + swir22)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result=stats(median, "NBR")
        return result

    #NEXT TASK CHECK WOFS ALGORYTHM
    #WOFS ALGORYTHM
    def flood_wofs(self,place, date1, date2, req_type):
        desired_collections = ["ls8_c2l2_sr"]
        odc_geom, desired_dates, datasets=self.check.checking(place, date1, date2, desired_collections, req_type)
        set_AWS()   #seecurity problem here! change this after finishing it working
        with rasterio.Env():
            ds = self.dc.load(
                product=desired_collections,
                datasets=datasets,  
                geopolygon=odc_geom,             
                time=desired_dates,
                output_crs="EPSG:32635",     
                resolution=(-30, 30),
                measurements=["red", "green", "blue", "nir08", "swir16", "swir22", "qa_pixel"],
                dask_chunks={"time": 1, "x": "auto", "y": "auto"},
                group_by="solar_day"
            )
        ds= ds.compute()
        sr_bands = ['red', 'green', 'blue', 'nir08', 'swir16', 'swir22']
        cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8",cover_types=['clear','water'], collection='c2', level='l2')
        qa = ds["qa_pixel"]
        dilated_cloud  = ((qa >> 1) & 1).astype(bool)
        cirrus         = ((qa >> 2) & 1).astype(bool)
        cloud_shadow   = ((qa >> 4) & 1).astype(bool)
        strict_mask =~dilated_cloud & ~cirrus & ~cloud_shadow
        nodata_mask = (ds[sr_bands] != 0).to_array(dim='band').all(dim='band')
        for band in sr_bands:
            ds[band] = ((ds[band] * 0.0000275 - 0.2) * 10000).clip(0, 10000).astype(np.int16)
        combined_mask = cloud_mask & nodata_mask & strict_mask
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
                scenes.append({"date": date, "status": "too_cloudy", "water_pct": None})
                continue   
            water_pct = round((clear_water / total_clear) * 100, 1)
            valid_so_far = [s for s in scenes if s["water_pct"] is not None]
            if valid_so_far:
                prev_water_pct = valid_so_far[-1]["water_pct"]
                if prev_water_pct-water_pct >= 40.0:
                    scenes.append({"date": date, "status": "too_cloudy", "water_pct": None})
                    continue

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
            "permanent_water":  f"{(water_frequency >= 95).mean().item() * 100:.2f}%",
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
    def sdd(self, place, date1, date2, req_type):
        desired_collections = ["sentinel_2_l2a"]
        odc_geom, desired_dates, datasets = self.check.checking(place, date1, date2, desired_collections, req_type)
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