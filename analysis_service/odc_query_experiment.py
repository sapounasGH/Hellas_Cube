from datacube import Datacube
import subprocess

dc = Datacube(app='example')

desired_date_range = ("2023-05-01", "2023-05-31")

# TODO expirement with HLS

ds = dc.load(
    product="sentinel_2_l2a",  
    x=(22.90, 22.95),
    y=(40.65, 40.7),
    crs="EPSG:4326",
    time=desired_date_range,
    measurements=["red",  "nir"],
    output_crs="EPSG:32635", 
    resolution=(-20, 20), 
    group_by='solar_day'
)

if not ds:
    print("No data found! staccing....")
    #bbbox
    x_min, x_max = (22.90, 22.95)
    y_min, y_max = (40.65, 40.7)
    bbox_str = f"{x_min},{y_min},{x_max},{y_max}"

    #dates
    date_str = f"{desired_date_range[0]}/{desired_date_range[1]}"

    #command
    command = [
        "/home/christossapounas/.conda/envs/odc_env/bin/stac-to-dc",
        "--catalog-href", "https://earth-search.aws.element84.com/v1",
        "--collections", "sentinel-2-l2a",
        "--bbox", bbox_str,
        "--datetime", date_str,
        "--rename-product", "sentinel_2_l2a" 
        ]

    #execution
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr="stac-to-dc failed")
    print("Done")

    #load the dataset
    ds = dc.load(
        product="sentinel_2_l2a",  
        x=(22.90, 22.95),
        y=(40.65, 40.7),
        crs="EPSG:4326",
        time=desired_date_range,
        measurements=["red",  "nir"],
        output_crs="EPSG:32635", 
        resolution=(-10, 10), 
        group_by='solar_day'
    )


red = ds["red"].astype("float32")
nir = ds["nir"].astype("float32")  
ndvi = (nir - red) / (nir + red)
calc_ndvi = ndvi.isel(time=0)
print(f"NDVI Mean : {calc_ndvi.mean().values:.3f}")