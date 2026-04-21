from datacube import Datacube
import warnings
warnings.filterwarnings('ignore')
import sys
from get_dataset import check_data
#for wofs
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask
import numpy as np

#WHAT I NEED TO DO:
dc = Datacube(app='Hellas_Cube')

def main():
   # we can change that and have a json that decodes the analyzation i want to do 
   if sys.argv[4] == "NDVI":
     ndvi(sys.argv[1], sys.argv[2], sys.argv[3])
   elif sys.argv[4] == "NDCI":
      ndci(sys.argv[1], sys.argv[2], sys.argv[3])
   elif sys.argv[4] == "NDTI":
      ndti(sys.argv[1], sys.argv[2], sys.argv[3])
   #A BIG IF to choose index  with the sys argv

def ndvi(place, date1, date2):
   desired_collections = ["sentinel_2_l2a"]
   odc_geom, desired_dates=check_data(place, date1, date2, desired_collections)
   ds = dc.load(
      product=desired_collections,  
      geopolygon=odc_geom,             
      time=desired_dates,
      output_crs="EPSG:32635",     
      resolution=(-10, 10),
      measurements=["red", "nir"]            
   )
   #NDVI INDEX
   red=ds["red"].astype("float32")
   nir=ds["nir"].astype("float32")  
   ndvi_index = (nir - red) / (nir + red)
   ndvi_index = ndvi_index.isel(time=0)
   ndvi_index=round(float(ndvi_index.mean().values), 3)
   print(ndvi_index)

#NDCI INDEX
def ndci(place,date1,date2):
   desired_collections = ["sentinel_2_l2a"]
   odc_geom, desired_dates=check_data(place, date1, date2, desired_collections)
   ds = dc.load(
      product=desired_collections,  
      geopolygon=odc_geom,             
      time=desired_dates,
      output_crs="EPSG:32635",     
      resolution=(-10, 10),
      measurements=["red", "rededge"]            
   )
   red=ds["red"].astype("float32")
   rededg1=ds["rededge"].astype("float32")  
   ndci_index = (rededg1 - red) / (rededg1 + red)
   ndci_index = ndci_index.isel(time=0)
   ndci_index=round(float(ndci_index.mean().values), 3)
   print(ndci_index)

#NDTI
def ndti(place,date1,date2):
   desired_collections = ["sentinel_2_l2a"]
   odc_geom, desired_dates=check_data(place, date1, date2, desired_collections)
   ds = dc.load(
      product=desired_collections,  
      geopolygon=odc_geom,             
      time=desired_dates,
      output_crs="EPSG:32635",     
      resolution=(-10, 10),
      measurements=["red", "rededge"]            
   )
   red=ds["red"].astype("float32")
   green=ds["green"].astype("float32")  
   ndti_index = (red - green) / (red + green)
   ndti_index = ndti_index.isel(time=0)
   ndti_index=round(float(ndti_index.mean().values), 3)
   print(ndti_index)

def flood_wofs(place, date1, date2):
   desired_collections = ["ls8_c2l2_sr"]
   odc_geom, desired_dates=check_data(place, date1, date2, desired_collections)
   ds = dc.load(
      product=desired_collections,  
      geopolygon=odc_geom,             
      time=desired_dates,
      output_crs="EPSG:32635",     
      resolution=(-30, 30),
      measurements=["red", "green", "blue", "nir", "swir1", "swir2", "qa_pixel"]    
   )
   #print(list(ds.data_vars))   # ← add this
   #print(ds)
   #renaming for the clean mask 
   #print("dataset loaded")
   cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8",cover_types=['clear', 'water'], collection='c2', level='l2')
   #print("Succesfull Cleaned!")

   #renaming for the wofs
   sr_bands = ['red', 'green', 'blue', 'nir', 'swir1', 'swir2']
   # NO DATA NO PROBLEMO
   for band in sr_bands:
      ds[band] = ((ds[band] * 0.0000275 - 0.2) * 10000).clip(0, 10000).astype(np.int16)
   nodata_mask = (ds[sr_bands] != 0).to_array(dim='band').all(dim='band')
   combined_mask = cloud_mask & nodata_mask
   #print("Starting WOFS")
   water_classification = wofs_classify(ds, x_coord="x", y_coord="y", clean_mask=combined_mask, no_data=255)
   #print("WOfS successfully classified the water!")

   water_classification_percentages = (
      water_classification.wofs
      .where(water_classification.wofs != 255)
      .mean(dim="time") * 100
   )

   #print(water_classification_percentages.mean().item()*100)
   #print("Calculated water classification percentages.")


   water_classification_percentages_05 = water_classification_percentages > 50
   percent_area_is_water = water_classification_percentages_05.mean().item() * 100
   print(
      f"Conclusion: Approximately {percent_area_is_water:.2f}% of this bounding box "
      f"is frequently covered by water (e.g., permanent river or lake)."
   )
   #apotelesma einai 0.00% enw tha eprepe na einai terastio...peiergo

if __name__=="__main__":
   main()