"""
File: constants.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: Constants contains all the variables and functions that are constants throughout the project
"""

class constants: 

    #Scale for sentinel-l2   
    S2_SCALE = 0.0001

    #RESOLUTIONS
    RES_10=(-10, 10)
    RES_20=(-20,20)
    RES_30=(-30,30)

    #Directory of the geojson, this may change
    GEOS_DIR="/home/christossapounas/Projects/Hellas_Cube/analysis_service/Geographic_data_maps"

    #SENTINEL
    SENTINEL=["sentinel_2_l2a"]

    #LANDSAT
    LANDSAT8=["ls8_c2l2_sr"]
    LANDSAT9=["ls9_c2l2_sr"]

    #HLS
    HLS_L=["hls_l30"]
    HLS_S=["hls_s30"]


    #COLORS FOR SENTINEL
    COASTAL="coastal" 
    BLUE="blue" 
    GREEN="green" 
    RED="red" 
    RED_EDGE_1="rededge1" 
    RED_EDGE_2="rededge2" 
    RED_EDGE_3="rededge3" 
    NIR="nir" 
    NIR08="nir08" 
    NIR09="nir09" 
    SWIR_16="swir16" 
    SWIR_22="swir22" 
    SCL="scl" 
    AOT="aot" 
    WVP="wvp" 

    #COLORS FOR LANDSAT
    LANDSAT_COASTAL="coastal" 
    LANDSAT_BLUE="blue" 
    LANDSAT_GREEN="green" 
    LANDSAT_RED="red" 
    LANDSAT_NIR="nir08" 
    LANDSAT_SWIR16="swir16" 
    LANDSAT_SWIR22="swir22" 
    LANDSAT_QA_AEROSOL="qa_aerosol" 
    LANDSAT_QA_PIXEL="qa_pixel" 
    LANDSAT_QA_RADSAT="qa_radsat" 

    #COLORS FOR HLS l30
    HLS_L30_COASTAL="B01" 
    HLS_L30_BLUE="B02" 
    HLS_L30_GREEN="B03" 
    HLS_L30_RED="B04" 
    HLS_L30_NIR="B05" 
    HLS_L30_SWIR1="B06" 
    HLS_L30_SWIR2="B07" 
    HLS_L30_CIRRUS="B09" 
    HLS_L30_TIR1="B10" 
    HLS_L30_TIR2="B11" 
    HLS_L30_SZA="SZA" 
    HLS_L30_SAA="SAA" 
    HLS_L30_VZA="VZA" 
    HLS_L30_VAA="VAA" 
    HLS_L30_FMASK="Fmask" 

    #COLORS FOR HLS s30
    HLS_S30_COASTAL="B01" 
    HLS_S30_BLUE="B02" 
    HLS_S30_GREEN="B03" 
    HLS_S30_RED="B04" 
    HLS_S30_RED_EDGE_1="B05" 
    HLS_S30_RED_EDGE_2="B06" 
    HLS_S30_RED_EDGE_3="B07" 
    HLS_S30_NIR_BROAD="B08" 
    HLS_S30_NIR_NARROW="B8A" 
    HLS_S30_WATER_VAPOR="B09" 
    HLS_S30_CIRRUS="B10" 
    HLS_S30_SWIR1="B11" 
    HLS_S30_SWIR2="B12" 
    HLS_S30_SZA="SZA" 
    HLS_S30_SAA="SAA" 
    HLS_S30_VZA="VZA" 
    HLS_S30_VAA="VAA" 
    HLS_S30_FMASK="Fmask" 
    
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
    FIND_WATER_MASK=[4,5,6,7]
    BURN_MASK=[2,4,5,7]
    VEGETATION_MOIST_MASK_BUILD=[4,5,7]
    SNOW_MASK=[5,7,11]
    WATER_MASK=[6,7]
    STRICT_MASK=[4,5,6,7,11]
    MEDIUM_MASK=[2,4,5,6,7,11]
    LOW_MASK=[]

    # HLS Fmask definitions (These represent the bit positions to EXCLUDE)

    F_STRICT_MASK = [0, 1, 2, 3] 

    F_BURN_MASK = [0, 1, 2, 3, 4, 5] 

    F_FIND_WATER_MASK = [0, 1, 2, 3, 4]

    # Landsat QA_PIXEL definitions (Bits to EXCLUDE)

    # Exclude dilated clouds, cirrus, clouds, and cloud shadows
    LANDSAT_STRICT_MASK = [1, 2, 3, 4] 

    # Exclude clouds, shadows, AND Snow
    LANDSAT_VEGETATION_MASK = [1, 2, 3, 4, 5] 

    # Exclude clouds, shadows, snow, AND Water (Land only)
    LANDSAT_BURN_MASK = [1, 2, 3, 4, 5, 7]

    #Constants for the stac-to-dc commant
    DIR_OF_COMMAND="/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc"
    CATALOG_URL="https://earth-search.aws.element84.com/v1"
    CATALOG_URL_HLS="https://cmr.earthdata.nasa.gov/stac/LPCLOUD"

    @staticmethod
    def staccing(catalog):
        STAC_MAP={
         "sentinel_2_l2a": "sentinel-2-l2a",
         "ls8_c2l2_sr": "landsat-c2-l2",
         "hls_l30":"HLSL30.v2.0",
         "hls_s30":"HLSS30.v2.0"
        }
        stac_collection = STAC_MAP.get(catalog)
        return stac_collection

    @staticmethod
    def url_conf(self, catalog):
        STAC_MAP={
         "sentinel_2_l2a": self.CATALOG_URL_HLS,
         "ls8_c2l2_sr": self.CATALOG_URL,
         "hls_l30": self.CATALOG_URL_HLS,
         "hls_s30":self.CATALOG_URL_HLS
        }
        stac_collection = STAC_MAP.get(catalog)
        return stac_collection

    #crs
    #global
    CRS_GLOBAL="EPSG:4326"

    #UTM Zone 35N, projected coordinates
    CRS_GREECE="EPSG:32635"


