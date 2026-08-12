"""
File: data_manager.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: This is the data manager, it helps us load the dataset, expoort statistics for our results
"""

from datacube import Datacube
from analysis_service.dataset_importer import check_data
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask
import numpy as np
import rasterio
from set_AWS import set_AWS
import xarray as xr
from constants import constants
from data_manager import data_manager
#import time

#ΝΑ ΕΦΑΡΜΌΣΩ ΌΛΕΣ ΤΙΣ ΔΥΝΑΤΌΤΗΤΕΣ ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΕΦΟΥΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΥ ΤΗΣ PYHON ΕΔΩ ΠΆΝΩ ΓΕΝΙΚΑ ΝΑ ΚΑΛΥΤΕΡ"ΤΗΝ ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΕΦΙΑ
#INDEXES TO CONVERT TO ODC INDEXES: NDWI
# AND INDEXES TO CONVERT TO ONLY WITH LANDSAT: NDWI
#WHERE TO ADD HLS: I THINK MAYBE TO ALL
#GENERAL ADD SAVI, EVI

class env_ind:

    #Constructor
    def __init__(self):
        #initialize Datacube as an object
        self.dc = Datacube(app='Hellas_Cube')

        #initialize a object for checking the data
        self.check=check_data(self.dc)

        #initializing the constants to get them throughout
        self.const=constants

        #initialize an object to manage the data
        self.data_manager=data_manager(self.dc, self.check)

    #A method for masking the data using SCL
    def mask_scl(ds, mask):
        return ds["scl"].isin(mask)

    #SENTINEL-2
    #NDVI(NORMALIZED DIFFRENCE VEGETATION INDEX)
    def ndvi(self,place, date1, date2, client, req_type):
        #load the dataset
        ds=self.data_manager.load_s2( place, 
                                      date1, 
                                      date2, 
                                      req_type, 
                                      [self.const.NIR, self.const.RED], 
                                      self.const.RES_10, 
                                      self.const.SENTINEL)
        
        #Mask the data
        mask=self.mask_scl(ds, self.const.STRICT_MASK)

        #check if data are empty
        if len(ds.time) == 0:
            return {"error": "no_data"}

        #load first color
        nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        #load second color
        red=(ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        #apply index
        index=((nir - red) / (nir + red)).clip(-1, 1)

        #compute the median, computing with multiple threads
        median=client.compute(index.median(dim="time"), sync=True)

        #get the stats 
        result=self.data_manager.stats(median, "NDVI")

        #return the resutls
        return result

    #NDCI(NORMALIZED DIFFRENCE CHLOROFYL INDEX)
    def ndci(self,place,date1,date2, client, req_type):

        ds=self.data_manager.load_s2(place, date1, date2, req_type, [self.const.RED_EDGE_1, self.const.RED], self.const.RES_10, self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.WATER_MASK)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        rededge1=(ds[self.const.RED_edge_1].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        red=(ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((rededge1 - red) / (rededge1 + red)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NDCI")

        return result

    #NDTI(NORMALIZED DIFFRENCE TURBIDITY INDEX)
    def ndti(self, place,date1,date2, client, req_type):

        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.RED, self.const.GREEN], self.const.RES_10, self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.WATER_MASK)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        red = (ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        green = (ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((red - green) / (red + green)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NDTI")

        return result
    
    #NDWI(NORMALIZED DIFFRENCE WATER INDEX) CHANGE IT AND CALCULATE BOTH NDWI (McFeeters) and NDWI (Gao style)
    def ndwi(self, place, date1, date2, client, req_type):
        #NDWI IS BETTER FOR LANDSAT DATA CHANGE IT!!!!!!!!!!!!!!!!!!!!!!!!!! Datacube Has Utilites for it
        #FIX NDWI GAO STYLE IS NDMI NO POINT IN THOSE 2
        #NDWI (McFeeters)
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.GREEN, self.const.NIR], self.const.RES_10, self.const.SENTINEL)
        mask=self.mask_scl(ds, self.const.WATER_MASK)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        green = (ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        nir = (ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((green - nir) / (green + nir)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result1=self.data_manager.stats(median, "NDWI (McFeeters)")
        #NDWI (Gao style)
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.NIR, self.const.SWIR_16], (-20, 20), self.const.SENTINEL)
        mask=self.mask_scl(ds, self.const.WATER_MASK)
        if len(ds.time) == 0:
            return {"error": "no_data"}
        nir = (ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        index=((nir - swir16) / (nir + swir16)).clip(-1, 1)
        median=client.compute(index.median(dim="time"), sync=True)
        result2=self.data_manager.stats(median, "NDWI (Gao style)")
        return {
            **self.data_manager.prefix_self.data_manager.stats(result1, "mcf"),
            **self.data_manager.prefix_self.data_manager.stats(result2, "gao"),
        }

    #NDMI(NORMALIZED DIFFRENCE MOISTURE INDEX)
    def ndmi(self, place,date1,date2, client, req_type):
        #percentage of the area tha is cover by water
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.NIR, self.const.SWIR_16], (-20, 20), self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.VEGETATION_MOIST_MASK_BUILD)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        nir = (ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((nir - swir16) / (nir + swir16)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NDMI")

        result["water_extent"] = f"{float((result['mean'] > 0) * 100):.2f}%"

        return result
    
    #NDBI(NORMALIZED DIFFRENCE Built-up INDEX)
    def ndbi(self, place,date1,date2, client, req_type):
        #NDBI WORKS BETTER FOR LANDSAT, MAKE CHANGES FOR BETTER RESUTLS, maybe a fix is the nir08 because our product for the ls8 the name of the band is name:nir08
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.SWIR_16, self.const.NIR], (-20, 20), self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.VEGETATION_MOIST_MASK_BUILD)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        swir16 = (ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        nir = (ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((swir16 - nir) / (swir16 + nir)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NDBI")

        return result
    
    #NDSI(NORMALIZED DIFFRENCE SNOW INDEX)
    def ndsi(self, place,date1,date2, client, req_type):
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.GREEN, self.const.SWIR_16], self.const.RES_10, self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.SNOW_MASK)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        green = (ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        swir16 = (ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((green - swir16) / (green + swir16)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NDSI")

        return result

    #NBR (Normalized Burn Ratio)
    def nbr(self, place,date1,date2, client, req_type):
        ds=self.data_manager.load_s2(self.dc, self.check, place, date1, date2, req_type, [self.const.NIR, self.const.SWIR_22], self.const.RES_10, self.const.SENTINEL)

        mask=self.mask_scl(ds, self.const.BURN_MASK)

        if len(ds.time) == 0:
            return {"error": "no_data"}
        
        nir = (ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)
        swir22 = (ds[self.const.SWIR_22].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

        index=((nir - swir22) / (nir + swir22)).clip(-1, 1)

        median=client.compute(index.median(dim="time"), sync=True)

        result=self.data_manager.stats(median, "NBR")

        return result

    #NEXT TASK CHECK WOFS ALGORYTHM
    #WOFS ALGORYTHM

    def flood_wofs(self, place, date1, date2, req_type):
        desired_collections = ["ls8_c2l2_sr"]
        odc_geom, desired_dates, datasets = self.check.checking(place, date1, date2, desired_collections, req_type)
        set_AWS()  # security problem here! change this after finishing it working

        with rasterio.Env():
            ds = self.dc.load(
                product=desired_collections,
                datasets=datasets,
                geopolygon=odc_geom,
                time=desired_dates,
                output_crs="EPSG:32635",
                resolution=(-30, 30),
                measurements=[self.const.RED, self.const.GREEN, "blue", "nir08", self.const.SWIR_16, self.const.SWIR_22, "qa_pixel"],
                dask_chunks={"time": 1, "x": "auto", "y": "auto"},
                group_by="solar_day"
            )
            ds = ds.compute()  # moved inside the context: actual I/O happens here

        sr_bands = ['red', 'green', 'blue', 'nir08', 'swir16', 'swir22']

        cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8", cover_types=['clear', 'water'], collection='c2', level='l2')
        qa = ds["qa_pixel"]
        dilated_cloud = ((qa >> 1) & 1).astype(bool)
        cloud        = ((qa >> 3) & 1).astype(bool)   # added: explicit cloud bit
        cirrus       = ((qa >> 2) & 1).astype(bool)
        cloud_shadow = ((qa >> 4) & 1).astype(bool)
        strict_mask = ~dilated_cloud & ~cloud & ~cirrus & ~cloud_shadow

        nodata_mask = (ds[sr_bands] != 0).to_array(dim='band').all(dim='band')

        for band in sr_bands:
            ds[band] = ((ds[band] * 0.0000275 - 0.2) * 10000).clip(0, 10000).astype(np.int16)

        combined_mask = cloud_mask & nodata_mask & strict_mask
        water_classification = wofs_classify(ds, x_coord="x", y_coord="y", clean_mask=combined_mask, no_data=255)
        wofs_stack = water_classification.wofs  # (time, y, x)

        # --- per-scene bookkeeping (diagnostics only, not used for the frequency self.data_manager.stats) ---
        scenes = []
        for i in range(len(wofs_stack.time)):
            scene = wofs_stack.isel(time=i)
            date = str(wofs_stack.time.isel(time=i).values)[:10]
            clear_water = int((scene == 1).sum().item())
            clear_not_water = int((scene == 0).sum().item())
            total_clear = clear_water + clear_not_water

            if total_clear < 100:
                scenes.append({"date": date, "status": "too_cloudy", "water_pct": None, "clear_px": total_clear})
                continue

            water_pct = round((clear_water / total_clear) * 100, 1)
            scenes.append({
                "date": date,
                "water_pct": water_pct,
                "clear_px": total_clear,
                "status": "dry" if water_pct < 25 else "healthy"
            })

        valid_scenes = [s for s in scenes if s["status"] != "too_cloudy"]
        dry_scenes = [s for s in valid_scenes if s["status"] == "dry"]

        dry_ratio = len(dry_scenes) / len(valid_scenes) if valid_scenes else 0

        # trend: μέσος όρος τελευταίων N scenes vs υπόλοιπο ιστορικό
        N = min(5, len(valid_scenes))
        recent = valid_scenes[-N:]
        recent_avg = sum(s["water_pct"] for s in recent) / len(recent) if recent else None
        historic_avg = sum(s["water_pct"] for s in valid_scenes) / len(valid_scenes) if valid_scenes else None

        if recent_avg is not None and historic_avg is not None and historic_avg > 0:
            drop_pct = (historic_avg - recent_avg) / historic_avg
        else:
            drop_pct = 0

        if dry_ratio >= 0.5:
            conclusion = "dried"
        elif drop_pct >= 0.3:
            conclusion = "drying_trend"
        else:
            conclusion = "healthy"

        # --- per-pixel temporal aggregation: this is the actual WOfS frequency map ---
        wet_count = (wofs_stack == 1).sum(dim="time")
        clear_obs = ((wofs_stack == 1) | (wofs_stack == 0)).sum(dim="time")
        valid_px = clear_obs > 0
        freq = xr.where(valid_px, wet_count / clear_obs, np.nan)  # 2D water frequency, one value per pixel

        n_valid_px = int(valid_px.sum().item())

        def pct_pixels_above(threshold_pct):
            if n_valid_px == 0:
                return "0.00%"
            hits = int(((freq >= threshold_pct / 100) & valid_px).sum().item())
            return f"{hits / n_valid_px * 100:.2f}%"

        return {
            # "scenes":           scenes,
            "permanent_water":  pct_pixels_above(95),
            "persistent_water": pct_pixels_above(80),
            "seasonal_water":   pct_pixels_above(50),
            "occasional_water": pct_pixels_above(25),
            "conclusion":       conclusion,
            "total_scenes":     len(scenes),
            "valid_scenes":     len(valid_scenes),
            "cloudy_scenes":    len(scenes) - len(valid_scenes),
            "valid_pixels":     n_valid_px,
            "confidence":       "low" if len(valid_scenes) < 3 else "high",
        }
    
    #WATER CLARITY ALGORYTHM CHANGE IT TO TSM
    def sdd(self, place, date1, date2, req_type):
        desired_collections = self.const.SENTINEL
        odc_geom, desired_dates, datasets = self.check.checking(place, date1, date2, desired_collections, req_type)
        ds = self.dc.load(
            product=desired_collections,
            datasets=datasets,
            geopolygon=odc_geom,
            time=desired_dates,
            output_crs="EPSG:32635",
            resolution=self.const.RES_10,
            measurements=["blue", self.const.GREEN, self.const.RED],
            dask_chunks={"time": 1, "x": "auto", "y": "auto"}
        )
        blue = ds["blue"].astype("float32") * 0.0001
        green = ds[self.const.GREEN].astype("float32") * 0.0001
        red = ds[self.const.RED].astype("float32") * 0.0001
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