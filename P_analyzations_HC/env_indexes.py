#import subprocess
#import geopandas as gpd
#from odc.geo.xr import write_cog
#from odc.stac import load
#import osmnx as ox
#import planetary_computer
#from pystac_client import Client
#from shapely.geometry import box
#from odc.geo.geom import Geometry
#import matplotlib
#import matplotlib.pyplot as plt
#matplotlib.use('Agg') #leme sto matplot na min kanei eikona (gia ta linux kiriws auto edw)
#warnigns 
from datacube import Datacube
import warnings
warnings.filterwarnings('ignore')
import sys
from get_dataset import check_data

#WHAT I NEED TO DO:
dc = Datacube(app='Hellas_Cube')

def main():
   #print("WE CHOOSE which indexes we are going to use")
   # we can change that and have a json that decodes the analyzation i want to do 
   if sys.argv[4] == "NDVI":
     ndvi(sys.argv[1], sys.argv[2], sys.argv[3])
   elif sys.argv[4] == "NDCI":
      ndci(sys.argv[1], sys.argv[2], sys.argv[3])
   elif sys.argv[4] == "NDTI":
      ndti(sys.argv[1], sys.argv[2], sys.argv[3])
   #A BIG IF to choose index  with the sys argv

#print("loading DATASET")

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

if __name__=="__main__":
   main()