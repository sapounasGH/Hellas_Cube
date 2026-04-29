import subprocess
import geopandas as gpd
from odc.geo.geom import Geometry
from dateutil import parser
#This function will ready the data for the Data Cube
#And checks on the DATABASE to add new indexes

class check_data:
   def __init__(self, dc):
      self.dc=dc

   def checking(self,place, date1, date2, catalog):
      #NEXT UPDATE CHANGE THE geojsons
      odc_geom, desired_aoi_geometry= self.get_odc_geom(place)
      #gia ena squere mias perioxis
      #desired_aoi_geometry=box(22.8, 40.6, 23.0, 40.7)
      #best alternate
      #gdf = ox.geocode_to_gdf("Kilkis, Greece", which_result=1)
      #desired_aoi_geometry = gdf.iloc[0].geometry

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
         print("Not found!")
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
         print(res.stderr)
      
      return odc_geom, desired_date_range

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
   
   def get_odc_geom(self, municipality:str):
      #this is not a static because i am going to change it 
      desired_aoi = gpd.read_file("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/Geographic_data_maps/municipalities.geojson")
      my_region = desired_aoi[desired_aoi['name:en'] == municipality]
      desired_aoi_geometry = my_region.iloc[0].geometry
      odc_geom = Geometry(desired_aoi_geometry, crs="EPSG:4326")
      return odc_geom, desired_aoi_geometry
      #from odc.geo import Geometry
      """
      from pathlib import Path
      GEOS_DIR="/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/Geographic_data_maps/"

      class geo_searcher:
         def __init__(self, geojson_dir: str):
         self._gdf=self._load_geos(geojson_dir)

         def _load_geos(directory:str):
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
            print(f"Loaded {len(merged)} features from {len(files)} files")
            return merged
            
      """
      #this will be built after building the internal python server