"""
File: data_manager.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: This is the data manager, it helps us load the dataset, expoort statistics for our results
"""

from datacube import Datacube
from analysis_service.dataset_loader import check_data
from constants import constants

class data_manager:

    def __init__(self, dc: Datacube, check: check_data):
        self.dc=dc
        self.check=check
        pass

    def load_s2(self, place: str, date1: str, date2: str, req_type: str, measurements: list,resolution: tuple, product: list):
    #loading the dataset need to do something diffrent for the resolution
        odc_geom, desired_dates, datasets = self.check.checking(place, date1, date2, ["sentinel_2_l2a"], req_type)   
        meas=list(dict.fromkeys(measurements + ["scl"]))  #adding scl, SCL is a way to mask the pixels
        ds=self.dc.load(
            product=product,
            datasets=datasets,
            geopolygon=odc_geom,
            time=desired_dates,
            output_crs=constants.CRS_GREECE,
            resolution=resolution,
            measurements=meas,
            dask_chunks={"time": 1, "x": 1024, "y": 1024},
            group_by="solar_day",
        )
        return ds

    def prefix_stats(d: dict, prefix: str) -> dict:
        return {f"{prefix}_{k}": v for k, v in d.items()}
    
    def stats(self, da: Datacube, index_name: str = "") -> dict:
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