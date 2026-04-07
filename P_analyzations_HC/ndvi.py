#for Open Data Cube
import subprocess
from datacube import Datacube
import geopandas as gpd
#from odc.geo.xr import write_cog
#from odc.stac import load
#import osmnx as ox
#import planetary_computer
#from pystac_client import Client
from shapely.geometry import box
from odc.geo.geom import Geometry
#import matplotlib
#import matplotlib.pyplot as plt
#matplotlib.use('Agg') #leme sto matplot na min kanei eikona (gia ta linux kiriws auto edw)
#warnigns 
import warnings
warnings.filterwarnings('ignore')
import sys

dc = Datacube(app='Hellas_Cube')

municipality = sys.argv[1]
#gia to aoi geojson:
desired_aoi = gpd.read_file("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/Geographic_data_maps/municipalities.geojson")
my_region = desired_aoi[desired_aoi['name:en'] == municipality]
desired_aoi_geometry = my_region.iloc[0].geometry

#gia ena squere mias perioxis
#desired_aoi_geometry=box(22.8, 40.6, 23.0, 40.7)

#best alternate
#gdf = ox.geocode_to_gdf("Kilkis, Greece", which_result=1)
#desired_aoi_geometry = gdf.iloc[0].geometry

#date poy theloume na ginei epeksergasia
desired_start_date = "2023-01-27"
desired_end_date = "2023-02-01"
desired_date_range = (desired_start_date, desired_end_date)
odc_geom = Geometry(desired_aoi_geometry, crs="EPSG:4326")

#travame apo tin microsoft dedomena apo to sentinel
#catalog_url = "https://earth-search.aws.element84.com/v1"
desired_collections = ["sentinel_2_l2a"]
datasetsfound=dc.find_datasets(
   product=desired_collections,
   geopolygon=odc_geom,
   time=desired_date_range
)
#if datasetsfound:
#    print(f"Dataset 1 actual measurement keys: {list(datasetsfound[0].measurements.keys())}")
#else:
#    print("No datasets found.")

if len(datasetsfound) == 0:
   #print("Not found!")
   minx, miny, maxx, maxy = desired_aoi_geometry.bounds
   bbox_str = f"{minx},{miny},{maxx},{maxy}"
   date_str = f"{desired_date_range[0]}/{desired_date_range[1]}"
   command = [
      "stac-to-dc",
      "--catalog-href", "https://earth-search.aws.element84.com/v1",
      "--collections", "sentinel-2-l2a",
      "--bbox", bbox_str,
      "--datetime", date_str
    ]
   subprocess.run(command, check=True)
#else: 
#   print(f"Found : {len(datasetsfound)} datasets")

#print("loading DATASET")
#datacube load
ds = dc.load(
   product=desired_collections,  
   geopolygon=odc_geom,             
   time=desired_date_range,
   output_crs="EPSG:32635",         
   resolution=(-10, 10),
   measurements=["red", "nir"]            
)
    
#print(ds)
#EPEKSERGASIA
#NDVI
red=ds["red"].astype("float32")
nir=ds["nir"].astype("float32")  
ndvi = (nir - red) / (nir + red)
first_day_ndvi = ndvi.isel(time=0)
print(f"NDVI Mean : {first_day_ndvi.mean().values:.3f}")

#NDTI
#red=ds["red"].astype("float32")
#green=ds["green"].astype("float32")  
#ndti = (red - green) / (red + green)
#Calc_ndti = ndti.isel(time=0)
#print(f"NDTI Mean is: {Calc_ndti.mean().values:.3f}")

#NDCI
#red=ds["red"].astype("float32")
#rededg1=ds["rededge"].astype("float32")  
#ndci = (rededg1 - red) / (rededg1 + red)
#Calc_ndci = ndci.isel(time=0)
#print(f"NDCI Mean is: {Calc_ndci.mean().values:.3f}")