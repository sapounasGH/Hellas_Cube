#from odc.geo.xr import write_cog
#from odc.stac import load
#import osmnx as ox
#import planetary_computer
#from pystac_client import Client
#from shapely.geometry import box
#import matplotlib
#import matplotlib.pyplot as plt
#matplotlib.use('Agg') #leme sto matplot na min kanei eikona (gia ta linux kiriws auto edw)
#import sys
import subprocess
from datacube import Datacube
import geopandas as gpd
from odc.geo.geom import Geometry
import parse_dates
import os
#This will ready the data for the Data Cube
#And checks on the DATABASE

def check_data(place, date1, date2, catalog):
   dc = Datacube(app='Hellas_Cube')
   municipality = place
   desired_aoi = gpd.read_file("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/Geographic_data_maps/municipalities.geojson")
   my_region = desired_aoi[desired_aoi['name:en'] == municipality]
   desired_aoi_geometry = my_region.iloc[0].geometry
   odc_geom = Geometry(desired_aoi_geometry, crs="EPSG:4326")

   #gia ena squere mias perioxis
   #desired_aoi_geometry=box(22.8, 40.6, 23.0, 40.7)

   #best alternate
   #gdf = ox.geocode_to_gdf("Kilkis, Greece", which_result=1)
   #desired_aoi_geometry = gdf.iloc[0].geometry

   #date poy theloume na ginei epeksergasia
   desired_start_date = parse_dates.convert_date(date1)
   desired_end_date = parse_dates.convert_date(date2)
   desired_date_range = (desired_start_date, desired_end_date)

   #travame apo tin microsoft dedomena apo to sentinel
   # EINAI AWS CATALOGOS
   #catalog_url = "https://earth-search.aws.element84.com/v1"
   desired_collections = catalog
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
      date_str = f"{parse_dates.convert_date2(desired_date_range[0])}/{parse_dates.convert_date2(desired_date_range[1])}"
      command = [
         "/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc",
         "--catalog-href", "https://earth-search.aws.element84.com/v1",
         "--collections", "sentinel-2-l2a",
         "--bbox", bbox_str,
         "--datetime", date_str
      ]
      subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr="SOMETHING WENT WRONG WITH THE STAC")
   
   return odc_geom, desired_date_range
   #else: 
   #   print(f"Found : {len(datasetsfound)} datasets")
      #else: 
      #   print(f"Found : {len(datasetsfound)} datasets")
