#for Open Data Cube
from datacube import Datacube
import geopandas as gpd
#from odc.geo.xr import write_cog
from odc.stac import load
import planetary_computer
from pystac_client import Client
from shapely.geometry import box
from odc.stac import load
#import matplotlib
#import matplotlib.pyplot as plt
#matplotlib.use('Agg') #leme sto matplot na min kanei eikona (gia ta linux kiriws auto edw)

#warnigns 
import warnings
warnings.filterwarnings('ignore')

dc = Datacube(app='example')

#gia to aoi geojson:
desired_aoi = gpd.read_file("aoi.geojson")
my_region = desired_aoi[desired_aoi['name'] == 'Crete']
desired_aoi_geometry = my_region.iloc[0].geometry

#gia ena squere mias perioxis
#desired_aoi_geometry=box(22.90, 40.65, 22.94, 40.68)

#date poy theloume na ginei epeksergasia
desired_start_date = "2023-01-27"
desired_end_date = "2023-02-01"
desired_date_range = (desired_start_date, desired_end_date)

#travame apo tin microsoft dedom;ena apo to sentinel
catalog_url = "https://planetarycomputer.microsoft.com/api/stac/v1/"
desired_collections = ["sentinel-2-l2a"]

#STAC
stac_client = Client.open(
   url=catalog_url,
   modifier=planetary_computer.sign_inplace,
)
items = stac_client.search(
    collections=desired_collections,
    intersects=desired_aoi_geometry,
    datetime=desired_date_range,
    query={"eo:cloud_cover": {"lt": 10}}
).item_collection()
#print(f"Found {len(items)} items")

#kaknoume load ta datasets
ds = dc.load(
   items=items,
   bands=["red", "green", "blue", "nir", "rededge"],#,"swir16", "swir22"
   geopolygon=desired_aoi_geometry,
   crs="utm",
   resolution=10
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