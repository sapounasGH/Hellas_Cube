import os
"""
THE DUMMY SETTING OF THE ENVIROMENTAL VARIABLES, set the 2 first
"""
def set_env_vars():

    #AWS AUTH
    os.environ["AWS_ACCESS_KEY_ID"] = ""                      # AWS access key (empty = anonymous/unsigned access)
    os.environ["AWS_SECRET_ACCESS_KEY"] = ""                  # AWS secret key (empty = anonymous/unsigned access)
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"            # region where the S3 bucket lives
    os.environ["AWS_REQUEST_PAYER"] = "requester"             #Just telling who pays (it's part of the error i encountered #REQEUSTER MUST ALWAYS PAY!)
    os.environ["AWS_NO_SIGN_REQUEST"] = "NO"                  # don't skip auth signing (requests will be signed, even though keys are blank)

    #NASA AUTH
    os.environ["GDAL_HTTP_COOKIEFILE"] = "/tmp/gdal_cookies.txt"   # where GDAL reads cookies from for auth
    os.environ["GDAL_HTTP_COOKIEJAR"] = "/tmp/gdal_cookies.txt"    # where GDAL writes/stores new cookies

    #general settings
    os.environ["GDAL_HTTP_MERGE_CONSECUTIVE_RANGES"] = "YES"  # merge S3 range requests
    os.environ["GDAL_HTTP_MULTIPLEX"] = "YES"                 # HTTP/2 multiplexing
    os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"  # skip directory listing
    os.environ["VSI_CACHE"] = "TRUE"                          # cache S3 reads
    os.environ["VSI_CACHE_SIZE"] = "10000000"                 # 10MB per file cache
    os.environ["CPL_VSIL_CURL_CACHE_SIZE"] = "200000000"      # 200MB global cache