import subprocess
import geopandas as gpd
from odc.geo.geom import Geometry
from shapely.geometry import shape
import json;
from dateutil import parser
from pathlib import Path
#This function will ready the data for the Data Cube
#And checks on the DATABASE to add new indexes
GEOS_DIR="/run/media/christossapounas/SAPOUNASUSB/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/Geographic_data_maps"
class check_data:
   def __init__(self, dc):
      self.dc=dc
      self.geoserch=geo_searcher(GEOS_DIR)._gdf

   def get_odc_geom_by_name(self, area: str):
      name_cols = [col for col in self.geoserch.columns if col == 'name' or col.startswith('name:')]
      mask = self.geoserch[name_cols].apply(
         lambda col: col.str.lower() == area.lower()
      ).any(axis=1)
      my_region = self.geoserch[mask]
      if my_region.empty:
         raise ValueError(f"Couldn't Find: {area}")
      desired_aoi_geometry = my_region.iloc[0].geometry
      odc_geom = Geometry(desired_aoi_geometry, crs="EPSG:4326")
      return odc_geom, desired_aoi_geometry
   
   def get_odc_geom_by_geojson(self, place: str):
      geojson = json.loads(place)
      desired_aoi_geometry = shape(geojson["features"][0]["geometry"])
      odc_geom = Geometry(desired_aoi_geometry, crs="EPSG:4326")
      return odc_geom, desired_aoi_geometry

   def checking(self,place, date1, date2, catalog, req_type):
      if (req_type=="DEFAULT"):
         #here we pass the geojson that we saved is saved in our database as a string and 
         odc_geom, desired_aoi_geometry= self.get_odc_geom_by_geojson(place)
      elif(req_type=="TARGET"):
         odc_geom, desired_aoi_geometry= self.get_odc_geom_by_name(place)
         #other than that we need to get the geojson and everything
         
      desired_start_date = self.convert_date(date1)
      desired_end_date = self.convert_date(date2)
      desired_date_range = (desired_start_date, desired_end_date)
      desired_collections = catalog #AWS CATALOG
      datasetsfound=self.dc.find_datasets(
         product=desired_collections,
         geopolygon=odc_geom,
         time=desired_date_range
      )
      if len(datasetsfound) == 0:
         print("Performing STAC-TO-DC.......to get indexes....")
         minx, miny, maxx, maxy = desired_aoi_geometry.bounds
         bbox_str = f"{minx},{miny},{maxx},{maxy}"
         date_str = f"{self.convert_date2(desired_date_range[0])}/{self.convert_date2(desired_date_range[1])}"
         command = [
            "/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc",
            "--catalog-href", "https://earth-search.aws.element84.com/v1",
            "--collections", self.staccing(catalog[0]),
            "--bbox", bbox_str,
            "--datetime", date_str,
            "--rename-product", catalog[0]
         ]
         res=subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
         print("Done")
         if(res.stderr):print(f"Error: {res.stderr}")
         datasetsfound=self.dc.find_datasets(
         product=desired_collections,
         geopolygon=odc_geom,
         time=desired_date_range
         )
      return odc_geom, desired_date_range, datasetsfound

   @staticmethod
   def staccing(catalog):
      STAC_MAP={
         "sentinel_2_l2a": "sentinel-2-l2a",
         "ls8_c2l2_sr": "landsat-c2-l2",
      }
      stac_collection = STAC_MAP.get(catalog)
      return stac_collection
   
   @staticmethod
   def convert_date(date_str: str, output_format: str = "%d-%m-%Y") -> str:
      return parser.parse(date_str).strftime(output_format)
   @staticmethod
   def convert_date2(date_str: str, output_format: str = "%Y-%m-%d") -> str:
      return parser.parse(date_str).strftime(output_format)

#This class is helping us merge and control the geojson file and load them
class geo_searcher:
   def __init__(self, geojson_dir: str):
      self._gdf=self._load_geos(geojson_dir)

   def _load_geos(self, directory:str):
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