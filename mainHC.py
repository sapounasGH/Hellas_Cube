#for Open Data Cube
from datacube import Datacube
import geopandas as gpd
#from odc.geo.xr import write_cog
from odc.stac import load
import planetary_computer
from pystac_client import Client
from shapely.geometry import box

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') #leme sto matplot na min kanei eikona (gia ta linux kiriws auto edw)

#for wofs(floods)
import numpy as np
import xarray as xr
from odc.algo import wofs_classify, keep_good_only
from utils.data_cube_utilities.clean_mask import landsat_qa_clean_mask

#warnigns 
import warnings
warnings.filterwarnings('ignore')

dc = Datacube(app='example')

#gia to aoi geojson:
#desired_aoi = gpd.read_file("aoi.geojson")
#my_region = desired_aoi[desired_aoi['name'] == 'Crete']
#desired_aoi_geometry = my_region.iloc[0].geometry

#gia ena squere mias perioxis
desired_aoi_geometry=box(22.90, 40.65, 22.94, 40.68)

#date poy theloume na ginei epeksergasia
desired_start_date = "2023-01-20"
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
print(f"Found {len(items)} items")

#kaknoume load ta datasets
ds = dc.load(
   items=items,
   bands=["red", "green", "blue", "nir","swir16", "swir22"],
   geopolygon=desired_aoi_geometry,
   crs="utm",
   resolution=10,
)
print(ds)
#EPEKSERGASIA
#NDVI
red=ds["red"].astype("float32")
nir=ds["nir"].astype("float32")  
ndvi = (nir - red) / (nir + red)
first_day_ndvi = ndvi.isel(time=0)
#print(f"NDVI Mean of Crete: {first_day_ndvi.mean().values:.3f}")

#flood with wofs
latitude_wofs = (1.0684, 0.8684)
longitude_wofs  = (-74.8409, -74.6409)
time_extents_wofs = ('2000-01-01', '2018-01-01')
platform_wofs = "LANDSAT_8"
product_wofs = 'ls8_collection1_AMA_ingest'
resolution_wofs = (-0.000269494585236, 0.000269494585236)
output_crs_wofs = 'EPSG:4326'
landsat_dataset_wofs = dc.load(
    latitude=latitude_wofs,
    longitude=longitude_wofs,
    platform=platform_wofs,
    time=time_extents_wofs,
    product=product_wofs,
    output_crs=output_crs_wofs,
    resolution=resolution_wofs,
    measurements=(
        'red',
        'green',
        'blue',
        'nir',
        'swir1',
        'swir2',
        'pixel_qa'
    )
) 
cloud_mask = landsat_qa_clean_mask(landsat_dataset_wofs, platform=platform_wofs)
cleaned_dataset = landsat_dataset_wofs.where(cloud_mask)
water_classification = wofs_classify(landsat_dataset_wofs, clean_mask=cloud_mask)
water_classification = water_classification.where(water_classification != -9999).astype(np.float16)
water_classification_percentages = (water_classification.mean(dim=['time']) * 100).wofs.rename('water_classification_percentages')
print(water_classification_percentages)
#take the >0.5 and take a mean about the percentages. make a conclusion about the river/lake/flooding etc
water_classification_percentages_05=water_classification_percentages>50
sum_pixles= water_classification_percentages_05.sum().values
wofs_conclusion=water_classification_percentages_05/sum_pixles
print(f"The average percantage of the water in this area is {wofs_conclusion:3f}")

#