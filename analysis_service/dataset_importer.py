"""
File: data_manager.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: This is the data importer, it is reliable for getting the data into our ODC database.
             depending on the data it receives, name or geojson of the area, it behaves accordingly
"""

import subprocess
import geopandas as gpd
from odc.geo.geom import Geometry
from shapely.geometry import shape
import json;
from dateutil import parser
from pathlib import Path
from constants import constants

class check_data:

   #constructor, getting the dc obejct of datacube and also setting the geosearch helper and constants
   def __init__(self, dc):
      self.dc=dc
      self.geoserch=geo_searcher(constants.GEOS_DIR)._gdf
      self.constants=constants

   #This method is realiable for the checking if the data exist in the database, if not , call @get_datasets
   def checking(self,place, date1, date2, catalog, req_type):
      if (req_type=="DEFAULT"):
         #getting the geom and geometry by receiving a geojson
         odc_geom, desired_aoi_geometry= self.get_by_geojson_of_aoi(place)
      elif(req_type=="TARGET"):
         #other than that we need to get the geojson only by the name of it
         odc_geom, desired_aoi_geometry= self.get_by_name_of_aoi(place)

      #Configuring the date range, collection
      desired_start_date = self.convert_date(date1)
      desired_end_date = self.convert_date(date2)
      desired_date_range = (desired_start_date, desired_end_date)
      desired_collections = catalog #AWS CATALOG

      #searching for existing dataset
      datasetsfound=self.dc.find_datasets(
         product=desired_collections,
         geopolygon=odc_geom,
         time=desired_date_range
      )

      #if we find no dataset, try to get them
      if len(datasetsfound) == 0:
         odc_geom, desired_date_range, datasetsfound= self.get_datasets(desired_aoi_geometry, 
                                                                        desired_date_range, 
                                                                        catalog,
                                                                        desired_collections,
                                                                        odc_geom)
      return odc_geom, desired_date_range, datasetsfound

   #Getting the datasets
   def get_datasets(self, desired_aoi_geometry, desired_date_range, catalog, desired_collections, odc_geom):
      print("Performing STAC-TO-DC.......to get indexes....for "+ catalog)

      #Defining geospacial area and dates
      minx, miny, maxx, maxy = desired_aoi_geometry.bounds
      bbox_str = f"{minx},{miny},{maxx},{maxy}"
      date_str = f"{self.convert_date2(desired_date_range[0])}/{self.convert_date2(desired_date_range[1])}"

      #actual command of stac-to-dc
      command = [
         constants.STAC_TO_DC,
         "--catalog-href", constants.url_conf(catalog[0]),
         "--collections", constants.staccing(catalog[0]),
         "--bbox", bbox_str,
         "--datetime", date_str,
         "--rename-product", catalog[0]
      ]
      res=subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
      if(res.stderr):
         print(f"Error: {res.stderr}")
         return

      #find the datasets we just 
      datasetsfound=self.dc.find_datasets(
         product=desired_collections,
         geopolygon=odc_geom,
         time=desired_date_range
      )
      print("STAC-TO-DC Executed SUccessfull")
      return odc_geom, desired_date_range, datasetsfound

   #getting the geom and the geometry only by the name of the area, accessing our geojson data from overpass.eu
   def get_by_name_of_aoi(self, area: str):
      name_cols = [col for col in self.geoserch.columns if col == 'name' or col.startswith('name:')]
      mask = self.geoserch[name_cols].apply(
         lambda col: col.str.lower() == area.lower()
      ).any(axis=1)
      my_region = self.geoserch[mask]
      if my_region.empty:
         raise ValueError(f"Couldn't Find: {area}")
      desired_aoi_geometry = my_region.iloc[0].geometry
      odc_geom = Geometry(desired_aoi_geometry, crs=self.constants.CRS_GLOBAL)
      return odc_geom, desired_aoi_geometry

   #accessing the geom and the geometry from a geojson we passed on
   def get_by_geojson_of_aoi (self, place: str):
      geojson = json.loads(place)
      desired_aoi_geometry = shape(geojson["features"][0]["geometry"])
      odc_geom = Geometry(desired_aoi_geometry, crs=self.constants.CRS_GLOBAL)
      return odc_geom, desired_aoi_geometry

   #date formaters
   @staticmethod
   def convert_date(date_str: str, output_format: str = "%d-%m-%Y") -> str:
      return parser.parse(date_str).strftime(output_format)
   
   @staticmethod
   def convert_date2(date_str: str, output_format: str = "%Y-%m-%d") -> str:
      return parser.parse(date_str).strftime(output_format)

#This class is helping us merge and control the geojson file and load them, basically merges them all into one
#usefull in get_odc_geom_by_name()
class geo_searcher:
   #constructor
   def __init__(self, geojson_dir: str):
      self._gdf=self._load_geos(geojson_dir)

   #loading geojson data
   def _load_geos(self, directory:str):
      #MERGING the data
      files = list(Path(directory).glob("*.geojson"))
      gdfs = []
      for f in files:
            try:
               gdf = gpd.read_file(f)
               gdf["_source_file"] = f.name
               gdfs.append(gdf)
            except Exception as e:
               print(f"Warning: could not load {f.name}: {e}")
      merged = gpd.pd.concat(gdfs, ignore_index=True)
      return merged