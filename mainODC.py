import warnings
import geopandas as gpd
from datacube import Datacube
from odc.geo.geom import Geometry
from shapely.geometry import box
warnings.filterwarnings('ignore')

dc = Datacube(app='example')
#desired_aoi = gpd.read_file("aoi.geojson")
#my_region = desired_aoi[desired_aoi['name'] == 'Crete']
#shapely_geom = my_region.iloc[0].geometry
#desired_aoi_geometry=box(22.8,40.6,23.0,40.7)

#desired_aoi_geometry = Geometry(shapely_geom, crs="EPSG:4326")
desired_date_range = ("2023-05-01", "2023-05-31")

print("Querying the Data Cube...")
ds = dc.load(
    product="sentinel_2_l2a",  
    x=(22.8, 23.0),
    y=(40.6, 40.7),
    crs="EPSG:4326",
    time=desired_date_range,
    measurements=["red", "green", "blue", "nir", "rededge1"],
    output_crs="EPSG:32635", 
    resolution=(-10, 10), 
    group_by='solar_day'
)

if not ds:
    print("No data found! Check your database indexing, product name, or time/spatial bounds.")
else:
    #print(f"Successfully loaded data: {ds}")
    # NDVI
    red = ds["red"].astype("float32")
    nir = ds["nir"].astype("float32")  
    ndvi = (nir - red) / (nir + red)
    calc_ndvi = ndvi.isel(time=0)
    print(f"NDVI Mean : {calc_ndvi.mean().values:.3f}")

    # NDTI
    green = ds["green"].astype("float32")  
    ndti = (red - green) / (red + green)
    calc_ndti = ndti.isel(time=0)
    print(f"NDTI Mean is: {calc_ndti.mean().values:.3f}")

    # NDCI
    rededge1 = ds["rededge1"].astype("float32")  
    ndci = (rededge1 - red) / (rededge1 + red)
    calc_ndci = ndci.isel(time=0)
    print(f"NDCI Mean is: {calc_ndci.mean().values:.3f}")

    #NDWI
    ndwi = (green - nir) / (green + nir)
    calc_ndwi = ndwi.isel(time=0)
    print(f"NDwI Mean is: {calc_ndwi.mean().values:.3f}")