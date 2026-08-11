"""
File: constants.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: Constants contains all the variables and functions that are constants throughout the project
"""

class constants: 

    #Scale for sentinel-l2   
    S2_SCALE = 0.0001

    #RESOLUTION
    RES_10=(-10, 10)

    #Directory of the geojson, this may change
    GEOS_DIR="/run/media/christossapounas/SAPOUNASUSB/Thesis_Hellas_Cube/Hellas_Cube/analysis_service/Geographic_data_maps"

    #SENTINEL
    SENTINEL=["sentinel_2_l2a"]

    #LANDSAT
    LANDSAT=[]
    #COLORS FOR SENTINEL
    NIR="nir"
    RED="red"
    GREEN="green"
    RED_EDGE_1="rededge1"
    SWIR_16="swir16"
    SWIR_22="swir22"


    #COLORS FOR LANDSAT
    
    #on the SCL scale
    """
    SCENE CLASSIFICATION TABLE
    | Label | Classification            |
    | 0     | NO_DATA                   |
    | 1     | SATURATED_OR_DEFECTIVE    |
    | 2     | DARK_AREA_PIXELS          |
    | 3     | CLOUD_SHADOWS             |
    | 4     | VEGETATION                |
    | 5     | NOT_VEGETATED             |
    | 6     | WATER                     |
    | 7     | UNCLASSIFIED              |
    | 8     | CLOUD_MEDIUM_PROBABILITY  |
    | 9     | CLOUD_HIGH_PROBABILITY    |
    | 10    | THIN_CIRRUS               |
    | 11    | SNOW                      |

    the main idea is that the masking is going to happen using the scl, SCENE CLASSIFICATION
    and the masking is 
    """
    #Masks for the dataset using the scl
    def find_water_scl_mask(ds):
        return ds["scl"].isin([4,5,6,7])

    def burn_scl_mask(ds):
        return ds["scl"].isin([2,4,5,7])

    def vegetation_moist_build_scl_mask(ds):
        return ds["scl"].isin([4,5,7])

    def only_snow_scl_mask(ds):
        return ds["scl"].isin([5,7,11])

    def water_inside_scl_mask(ds):
        return ds["scl"].isin([6,7])

    def strict_scl_mask(ds):
        return ds["scl"].isin([4,5,6,7,11])

    def medium_scl_mask(ds):
        return ds["scl"].isin([2,4,5,6,7,11])

    def low_scl_mask(ds):
        return ds["scl"].isin([])

    #Constants for the stac-to-dc commant
    DIR_OF_COMMAND="/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc"
    CATALOG_URL="https://earth-search.aws.element84.com/v1"

    @staticmethod
    def staccing(catalog):
        STAC_MAP={
         "sentinel_2_l2a": "sentinel-2-l2a",
         "ls8_c2l2_sr": "landsat-c2-l2",
        }
        stac_collection = STAC_MAP.get(catalog)
        return stac_collection

    #crs
    #global
    CRS_GLOBAL="EPSG:4326"

    #UTM Zone 35N, projected coordinates
    CRS_GREECE="EPSG:32635"


