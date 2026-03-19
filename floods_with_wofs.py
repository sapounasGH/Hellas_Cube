from datacube import Datacube

#for wofs(floods)
import numpy as np
import xarray as xr
from odc.algo import keep_good_only
# Apply WOFS water classification. Only consider non-cloudy pixels
from utils.data_cube_utilities.data_cube_utilities.dc_water_classifier import wofs_classify
from utils.data_cube_utilities.data_cube_utilities.clean_mask import landsat_qa_clean_mask



dc = Datacube(app='example')

#flood with wofs
latitude_wofs = (1.0684, 0.8684)
longitude_wofs  = (-74.8409, -74.6409)
time_extents_wofs = ('2015-01-01', '2018-01-01')
platform_wofs = "LANDSAT_8"
product_wofs = 'landsat-c2-l2'
resolution_wofs = (-0.000269494585236, 0.000269494585236)
output_crs_wofs = 'EPSG:4326'
ds = dc.load(
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
cloud_mask = landsat_qa_clean_mask(ds, platform="LANDSAT_8")
water_classification = wofs_classify(ds, clean_mask=cloud_mask, no_data=255)
print("WOfS successfully classified the water!")
water_classification_percentages = (water_classification.mean(dim=['time']) * 100).wofs.rename('water_classification_percentages')
print(water_classification_percentages)
#take the >0.5 and take a mean about the percentages. make a conclusion about the river/lake/flooding etc
water_classification_percentages_05=water_classification_percentages>50
sum_pixles= water_classification_percentages_05.sum().values
wofs_conclusion=water_classification_percentages_05/sum_pixles
print(f"The average percantage of the water in this area is {wofs_conclusion:3f}")