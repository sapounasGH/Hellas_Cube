from pystac_client import Client
from odc.stac import load
from datacube import Datacube
import numpy as np
import xarray as xr
import planetary_computer
from shapely.geometry import box
import geopandas as gpd
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask

#CHANNGE THIS AND DON"T USE STAC

dc = Datacube(app='example')
catalog_url = "https://planetarycomputer.microsoft.com/api/stac/v1/"
desired_collections = ["landsat-c2-l2"]

desired_aoi = gpd.read_file("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/specific_squere.geojson")
desired_aoi_geometry = desired_aoi.iloc[0].geometry

desired_start_date = "2019-01-27"
desired_end_date = "2021-02-01"
desired_date_range = (desired_start_date, desired_end_date)
#STAC
stac_client = Client.open(
   url=catalog_url,
   modifier=planetary_computer.sign_inplace,
)
items = stac_client.search(
    collections=desired_collections,
    intersects=desired_aoi_geometry,
    datetime=desired_date_range,
    query={"eo:cloud_cover": {"lt": 10},
           "platform": {"in": ["landsat-8"]}
           }
).item_collection()
#print(f"Found {len(items)} items")

#kaknoume load ta datasets

ds = load(
    items=items,
    bands=["red", "green", "blue", "nir08", "swir16", "swir22", "qa_pixel"],
   geopolygon=desired_aoi_geometry,
   crs="utm",
   resolution=10
)

#renaming for the clean mask 
#print("dataset loaded")
ds = ds.rename({
    "nir08":  "nir",
    "swir16": "swir1",
    "swir22": "swir2",
})
cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8",cover_types=['clear', 'water'], collection='c2', level='l2')
#print("Succesfull Cleaned!")

#renaming for the wofs
ds = ds.rename({
    "nir":  "nir08",
    "swir1": "swir16",
    "swir2": "swir22",
})

sr_bands = ['red', 'green', 'blue', 'nir08', 'swir16', 'swir22']
nodata_mask = ds['red'] == 0
for band in sr_bands:
    ds[band] = ((ds[band] * 0.0000275 - 0.2) * 10000).clip(0, 10000).astype(np.int16)
#print("Starting WOFS")
water_classification = wofs_classify(ds, x_coord="x", y_coord="y", clean_mask=cloud_mask, no_data=255)
#print("WOfS successfully classified the water!")

water_classification_percentages = (
    water_classification.wofs
    .where(water_classification.wofs != 255)
    .mean(dim="time") * 100
).rename("water_classification_percentages")

#print(water_classification_percentages.mean().item()*100)
#print("Calculated water classification percentages.")


water_classification_percentages_05 = water_classification_percentages > 50
percent_area_is_water = water_classification_percentages_05.mean().item() * 100
print(
    f"Conclusion: Approximately {percent_area_is_water:.2f}% of this bounding box "
    f"is frequently covered by water (e.g., permanent river or lake)."
)
#apotelesma einai 0.00% enw tha eprepe na einai terastio...peiergo