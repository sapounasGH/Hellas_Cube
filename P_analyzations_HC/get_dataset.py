import subprocess
from datacube import Datacube
import geopandas as gpd
from odc.geo.geom import Geometry
import parse_dates
#This function will ready the data for the Data Cube
#And checks on the DATABASE to add new indexes

def check_data(place, date1, date2, catalog):
   dc = Datacube(app='Hellas_Cube')
   #NEXT UPDATE CHANGE THE geojsons
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

   desired_start_date = parse_dates.convert_date(date1)
   desired_end_date = parse_dates.convert_date(date2)
   desired_date_range = (desired_start_date, desired_end_date)
   desired_collections = catalog #AWS CATALOG
   datasetsfound=dc.find_datasets(
      product=desired_collections,
      geopolygon=odc_geom,
      time=desired_date_range
   )

   if len(datasetsfound) == 0:
      print("Not found!")
      minx, miny, maxx, maxy = desired_aoi_geometry.bounds
      bbox_str = f"{minx},{miny},{maxx},{maxy}"
      date_str = f"{parse_dates.convert_date2(desired_date_range[0])}/{parse_dates.convert_date2(desired_date_range[1])}"
      command = [
         "/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc",
         "--catalog-href", "https://earth-search.aws.element84.com/v1",
         "--collections", staccing(catalog[0]),
         "--bbox", bbox_str,
         "--datetime", date_str,
         "--rename-product", catalog[0]
      ]
      res=subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
      print(res.stderr)
   
   return odc_geom, desired_date_range

def staccing(catalog):
   STAC_MAP={
      "sentinel_2_l2a": "sentinel-2-l2a",
      "ls8_c2l2_sr": "landsat-c2-l2",
   }
   stac_collection = STAC_MAP.get(catalog)
   return stac_collection