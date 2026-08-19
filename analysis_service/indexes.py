"""
File: data_manager.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: This is the data manager, it helps us load the dataset, expoort statistics for our results
"""
from dataset_importer import check_data
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask
import numpy as np
import xarray as xr
from data_manager import data_manager
from base_odc_service import BaseODCService
#import time

#ΝΑ ΕΦΑΡΜΌΣΩ ΌΛΕΣ ΤΙΣ ΔΥΝΑΤΌΤΗΤΕΣ ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΕΦΟΥΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΥ ΤΗΣ PYHON ΕΔΩ ΠΆΝΩ ΓΕΝΙΚΑ ΝΑ ΚΑΛΥΤΕΡ"ΤΗΝ ΑΝΤΙΚΕΙΜΕΝΟΣΤΡΕΦΙΑ
#INDEXES TO CONVERT TO ODC INDEXES: NDWI
# AND INDEXES TO CONVERT TO ONLY WITH LANDSAT: NDWI
#WHERE TO ADD HLS: I THINK MAYBE TO ALL
#GENERAL ADD SAVI, EVI


class env_ind(BaseODCService):

    #Constructor
    def __init__(self):
        #initialize Datacube as an object
        super().__init__()

        #initialize a object for checking the data
        self.check=check_data(self.dc)

        #initialize an object to manage the data
        self.data_manager=data_manager(self.dc, self.check)

    def mask_scl(self, ds, mask):
        return ds["scl"].isin(mask)
    
    def fmask(self, ds, exclude_bits):
        #Convert the list of bit positions 
        bit_mask = 0
        for bit in exclude_bits:
            bit_mask |= (1 << bit)
            
        # Extract the Fmask array and ensure it is an integer type for bitwise math
        fmask = ds[self.const.HLS_L30_FMASK].astype("int16")
        
        # Apply bitwise AND 
        valid_pixels = (fmask & bit_mask) == 0
        
        return valid_pixels

    def mask_landsat(self, ds, cover_types, platform="LANDSAT_8", collection='c2', level='l2'):
        return landsat_qa_clean_mask(
            ds,
            platform=platform,
            cover_types=cover_types,
            collection=collection,
            level=level
        )

    #NDVI(NORMALIZED DIFFRENCE VEGETATION INDEX)
    def ndvi(self, place, date1, date2, client, req_type, source):
        
        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.NIR, self.const.RED], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.STRICT_MASK)


            #load first color
            nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            red=(ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((nir - red) / (nir + red)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_NIR, self.const.LANDSAT_RED, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_STRICT_MASK)

            # Apply Landsat specific scale and offset
            nir = ((ds[self.const.LANDSAT_NIR].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            red = ((ds[self.const.LANDSAT_RED].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((nir - red) / (nir + red)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    nir_band, red_band, fmask_band = self.const.HLS_L30_NIR, self.const.HLS_L30_RED, self.const.HLS_L30_FMASK
                else:
                    nir_band, red_band, fmask_band = self.const.HLS_S30_NIR, self.const.HLS_S30_RED, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[nir_band, red_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                nir = (ds[nir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                red = (ds[red_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((nir - red) / (nir + red)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDVI")

        #return the resutls
        return result

    #NDCI(NORMALIZED DIFFRENCE CHLOROFYL INDEX)
    def ndci(self,place,date1,date2, client, req_type, source):
        # SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.RED_EDGE_1, self.const.RED], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.STRICT_MASK)


            #load first color
            rededge1=(ds[self.const.RED_EDGE_1].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            red=(ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((rededge1 - red) / (rededge1 + red)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # HLS (S30)
        elif source == "hls":
            index_arrays = []
            
            for product in self.const.HLS_S:
                rededge_band, red_band, fmask_band = self.const.HLS_S30_RED_EDGE_1, self.const.HLS_S30_RED, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[rededge_band, red_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                rededge = (ds[rededge_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                red = (ds[red_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((rededge - red) / (rededge + red)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        # error handle
        else:
            return {"error": "invalid_source"}

        #get the stats 
        result=self.data_manager.stats(index, "NDCI")

        #return the resutls
        return result

    #NDTI(NORMALIZED DIFFRENCE TURBIDITY INDEX)
    def ndti(self, place, date1, date2, client, req_type, source):
        
        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.RED, self.const.GREEN], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.WATER_MASK)


            #load first color
            red=(ds[self.const.RED].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            green=(ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((red - green) / (red + green)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_RED, self.const.LANDSAT_GREEN, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_STRICT_MASK)

            # Apply Landsat specific scale and offset
            red = ((ds[self.const.LANDSAT_RED].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            green = ((ds[self.const.LANDSAT_GREEN].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((red - green) / (red + green)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    red_band, green_band, fmask_band = self.const.HLS_L30_RED, self.const.HLS_L30_GREEN, self.const.HLS_L30_FMASK
                else:
                    red_band, green_band, fmask_band = self.const.HLS_S30_RED, self.const.HLS_S30_GREEN, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[red_band, green_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                red = (ds[red_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                green = (ds[green_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((red - green) / (red + green)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDTI")

        #return the resutls
        return result
    
    #NDWI(NORMALIZED DIFFRENCE WATER INDEX) - McFeeters
    def ndwi(self, place, date1, date2, client, req_type, source):

        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.GREEN, self.const.NIR], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.WATER_MASK)

            #load first color
            green=(ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((green - nir) / (green + nir)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_GREEN, self.const.LANDSAT_NIR, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_STRICT_MASK)

            # Apply Landsat specific scale and offset
            green = ((ds[self.const.LANDSAT_GREEN].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            nir = ((ds[self.const.LANDSAT_NIR].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((green - nir) / (green + nir)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    green_band, nir_band, fmask_band = self.const.HLS_L30_GREEN, self.const.HLS_L30_NIR, self.const.HLS_L30_FMASK
                else:
                    green_band, nir_band, fmask_band = self.const.HLS_S30_GREEN, self.const.HLS_S30_NIR, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[green_band, nir_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                green = (ds[green_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                nir = (ds[nir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((green - nir) / (green + nir)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDWI")

        #return the resutls
        return result

    #NDMI(NORMALIZED DIFFRENCE MOISTURE INDEX)
    def ndmi(self, place, date1, date2, client, req_type, source):

        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.NIR, self.const.SWIR_16], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.VEGETATION_MOIST_MASK_BUILD)

            #load first color
            nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            swir16=(ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((nir - swir16) / (nir + swir16)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_NIR, self.const.LANDSAT_SWIR16, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_VEGETATION_MASK)

            # Apply Landsat specific scale and offset
            nir = ((ds[self.const.LANDSAT_NIR].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            swir16 = ((ds[self.const.LANDSAT_SWIR16].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((nir - swir16) / (nir + swir16)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    nir_band, swir_band, fmask_band = self.const.HLS_L30_NIR, self.const.HLS_L30_SWIR1, self.const.HLS_L30_FMASK
                else:
                    nir_band, swir_band, fmask_band = self.const.HLS_S30_NIR, self.const.HLS_S30_SWIR1, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[nir_band, swir_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                nir = (ds[nir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                swir16 = (ds[swir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((nir - swir16) / (nir + swir16)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDMI")

        result["water_extent"] = f"{float((result['mean'] > 0) * 100):.2f}%"

        #return the resutls
        return result
    
    #NDBI(NORMALIZED DIFFRENCE Built-up INDEX)
    def ndbi(self, place, date1, date2, client, req_type, source):

        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.SWIR_16, self.const.NIR], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.VEGETATION_MOIST_MASK_BUILD)

            #load first color
            swir16=(ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((swir16 - nir) / (swir16 + nir)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_SWIR16, self.const.LANDSAT_NIR, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_STRICT_MASK)

            # Apply Landsat specific scale and offset
            swir16 = ((ds[self.const.LANDSAT_SWIR16].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            nir = ((ds[self.const.LANDSAT_NIR].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((swir16 - nir) / (swir16 + nir)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    swir_band, nir_band, fmask_band = self.const.HLS_L30_SWIR1, self.const.HLS_L30_NIR, self.const.HLS_L30_FMASK
                else:
                    swir_band, nir_band, fmask_band = self.const.HLS_S30_SWIR1, self.const.HLS_S30_NIR, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[swir_band, nir_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                swir16 = (ds[swir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                nir = (ds[nir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((swir16 - nir) / (swir16 + nir)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDBI")

        #return the resutls
        return result
    
    #NDSI(NORMALIZED DIFFRENCE SNOW INDEX)
    def ndsi(self, place, date1, date2, client, req_type, source):

        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.GREEN, self.const.SWIR_16], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.SNOW_MASK)

            #load first color
            green=(ds[self.const.GREEN].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            swir16=(ds[self.const.SWIR_16].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((green - swir16) / (green + swir16)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_GREEN, self.const.LANDSAT_SWIR16, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_STRICT_MASK)

            # Apply Landsat specific scale and offset
            green = ((ds[self.const.LANDSAT_GREEN].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            swir16 = ((ds[self.const.LANDSAT_SWIR16].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((green - swir16) / (green + swir16)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    green_band, swir_band, fmask_band = self.const.HLS_L30_GREEN, self.const.HLS_L30_SWIR1, self.const.HLS_L30_FMASK
                else:
                    green_band, swir_band, fmask_band = self.const.HLS_S30_GREEN, self.const.HLS_S30_SWIR1, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[green_band, swir_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                green = (ds[green_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                swir16 = (ds[swir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((green - swir16) / (green + swir16)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NDSI")

        #return the resutls
        return result

    #NBR (Normalized Burn Ratio)
    def nbr(self, place, date1, date2, client, req_type, source):
        #SENTINEL
        if source == "sentinel":
            #load the dataset
            ds=self.data_manager.load_s2( place, 
                                        date1, 
                                        date2, 
                                        req_type, 
                                        [self.const.NIR, self.const.SWIR_22], 
                                        self.const.RES_10, 
                                        self.const.SENTINEL)

            #check if data are empty
            if len(ds.time) == 0:
                return {"error": "no_data"}
                        
            #Mask the data
            mask=self.mask_scl(ds, self.const.BURN_MASK)

            #load first color
            nir=(ds[self.const.NIR].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #load second color
            swir22=(ds[self.const.SWIR_22].astype("float32") * self.const.S2_SCALE).where(mask).where(lambda x: x > 0)

            #apply index
            index=((nir - swir22) / (nir + swir22)).clip(-1, 1)

            #compute the median, computing with multiple threads
            index = client.compute(index, sync=True)

        # LANDSAT (Native)
        elif source == "landsat":
            ds = self.data_manager.load_dataset_with_env(
                place=place, date1=date1, date2=date2, req_type=req_type, 
                measurements=[self.const.LANDSAT_NIR, self.const.LANDSAT_SWIR22, self.const.LANDSAT_QA_PIXEL], 
                resolution=self.const.RES_30, 
                product= self.const.LANDSAT8
            )
            
            if ds is None or len(ds.time) == 0:
                return {"error": "no_data"}

            # Mask using the QA_PIXEL algorythm
            mask = self.mask_landsat(ds, self.const.LANDSAT_BURN_MASK)

            # Apply Landsat specific scale and offset
            nir = ((ds[self.const.LANDSAT_NIR].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            swir22 = ((ds[self.const.LANDSAT_SWIR22].astype("float32") * self.const.LANDSAT_SCALE) + self.const.LANDSAT_OFFSET).where(mask).where(lambda x: x > 0)
            
            index = ((nir - swir22) / (nir + swir22)).clip(-1, 1)
            index = index.compute()

        # HLS (L30 + S30)
        elif source == "hls":
            index_arrays = []
            
            for product in (self.const.HLS_L + self.const.HLS_S):
                if product in self.const.HLS_L:
                    nir_band, swir_band, fmask_band = self.const.HLS_L30_NIR, self.const.HLS_L30_SWIR2, self.const.HLS_L30_FMASK
                else:
                    nir_band, swir_band, fmask_band = self.const.HLS_S30_NIR, self.const.HLS_S30_SWIR2, self.const.HLS_S30_FMASK

                ds = self.data_manager.load_dataset_with_env(
                    place=place, date1=date1, date2=date2, req_type=req_type, 
                    measurements=[nir_band, swir_band, fmask_band], 
                    resolution=self.const.RES_30, product=[product]
                )
                
                if ds is None or len(ds.time) == 0:
                    continue

                # Mask using the Fmask algorythm
                mask = self.fmask(ds, self.const.F_STRICT_MASK)
                
                nir = (ds[nir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                swir22 = (ds[swir_band].astype("float32") * self.const.HLS_SCALE).where(mask).where(lambda x: x > 0)
                
                product_index = ((nir - swir22) / (nir + swir22)).clip(-1, 1)
                index_arrays.append(product_index)

            if not index_arrays:
                return {"error": "no_data"}

            # Combine the arrays and compute
            index = xr.concat(index_arrays, dim="time")
            index = index.compute()

        #error handling
        else:
            return {"error": "invalid_source"}

        #get the stats, unifying the output as one
        result=self.data_manager.stats(index, "NBR")

        #return the resutls
        return result
    
    #WOFS ALGORYTHM
    def flood_wofs(self, place, date1, date2, req_type):
        #define desired collections
        desired_collections = self.const.LANDSAT8         

        #load the dataset
        ds=self.data_manager.load_dataset_with_env(place, 
                                                    date1, 
                                                    date2, 
                                                    req_type, 
            [self.const.LANDSAT_RED, self.const.LANDSAT_GREEN, self.const.LANDSAT_BLUE, self.const.LANDSAT_NIR, self.const.LANDSAT_SWIR16, self.const.LANDSAT_SWIR22, self.const.LANDSAT_QA_PIXEL],
                                                    self.const.RES_30, 
                                                    desired_collections)
        
        #compute dataset into memory
        ds.compute()

        #define surface reflectance bands
        sr_bands =[self.const.LANDSAT_RED, self.const.LANDSAT_GREEN, self.const.LANDSAT_BLUE, self.const.LANDSAT_NIR, self.const.LANDSAT_SWIR16, self.const.LANDSAT_SWIR22]

        # generate cloud and quality masks
        cloud_mask = self.mask_landsat(ds, cover_types=['clear', 'water'], platform="LANDSAT_8", collection='c2', level='l2')

        # strict mask reusing the same QA_PIXEL bit definitions as every other index (dilated cloud, cirrus, cloud, cloud shadow)
        strict_mask = self.mask_landsat(ds, cover_types=self.const.LANDSAT_STRICT_MASK, platform="LANDSAT_8")

        #create no-data mask
        nodata_mask = (ds[sr_bands] != 0).to_array(dim='band').all(dim='band')

        #apply scaling factors to bands
        int_scale = int(10000)
        for band in sr_bands:
            ds[band] = ((ds[band] * self.const.LANDSAT_SCALE + self.const.LANDSAT_OFFSET) * int_scale).clip(0, int_scale).astype(np.int16)

        #combine all masks
        combined_mask = cloud_mask & nodata_mask & strict_mask
        
        #apply WOfS classification algorithm
        water_classification = wofs_classify(ds, x_coord="x", y_coord="y", clean_mask=combined_mask, no_data=255)
        
        #extract WOfS stack
        wofs_stack = water_classification.wofs  # (time, y, x)

        #calculate per-scene statistics (diagnostics only)
        scenes = []
        for i in range(len(wofs_stack.time)):
            scene = wofs_stack.isel(time=i)
            date = str(wofs_stack.time.isel(time=i).values)[:10]
            clear_water = int((scene == 1).sum().item())
            clear_not_water = int((scene == 0).sum().item())
            total_clear = clear_water + clear_not_water

            #skip if scene is too cloudy
            if total_clear < 150:
                scenes.append({"date": date, "status": "too_cloudy", "water_pct": None, "clear_px": total_clear})
                continue

            #compute water percentage for scene
            water_pct = round((clear_water / total_clear) * 100, 1)
            scenes.append({
                "date": date,
                "water_pct": water_pct,
                "clear_px": total_clear,
                "status": "dry" if water_pct < 25 else "healthy"
            })

        #filter valid scenes and dry scenes
        valid_scenes = [s for s in scenes if s["status"] != "too_cloudy"]
        dry_scenes = [s for s in valid_scenes if s["status"] == "dry"]

        #calculate dry ratio
        dry_ratio = len(dry_scenes) / len(valid_scenes) if valid_scenes else 0

        #calculate historic vs recent drying trend
        N = min(5, len(valid_scenes))
        recent = valid_scenes[-N:]
        recent_avg = sum(s["water_pct"] for s in recent) / len(recent) if recent else None
        historic_avg = sum(s["water_pct"] for s in valid_scenes) / len(valid_scenes) if valid_scenes else None

        if recent_avg is not None and historic_avg is not None and historic_avg > 0:
            drop_pct = (historic_avg - recent_avg) / historic_avg
        else:
            drop_pct = 0

        #determine conclusion status
        if dry_ratio >= 0.5:
            conclusion = "dried"
        elif drop_pct >= 0.3:
            conclusion = "drying_trend"
        else:
            conclusion = "healthy"

        #calculate temporal water frequency per pixel
        wet_count = (wofs_stack == 1).sum(dim="time")
        clear_obs = ((wofs_stack == 1) | (wofs_stack == 0)).sum(dim="time")
        valid_px = clear_obs > 0
        freq = xr.where(valid_px, wet_count / clear_obs, np.nan) 

        #count valid pixels
        n_valid_px = int(valid_px.sum().item())

        #define helper for threshold calculation
        def pct_pixels_above(threshold_pct):
            if n_valid_px == 0:
                return "0.00%"
            hits = int(((freq >= threshold_pct / 100) & valid_px).sum().item())
            return f"{hits / n_valid_px * 100:.2f}%"

        #return the results
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