pub mod help;
pub mod ndi;
pub mod user;
use crate::cli::{Args, Command, Config};
use std::{fs};  //, path::PathBuf
use toml;
use crate::commands::user::get_api_key;

pub fn matching(args: Args)-> Result<(), &'static str>{
    match args.command{
        Command::Help {}=>{
            help::run()
        }
        Command::Cacc { email, password }=>{
            match user::cacc(&email, &password) {
                Ok(()) =>{
                    println!("User created!");
                    println!("Email: {}", email);
                    println!("Password: {}", password)
                },
                Err(e) => println!("Something went wrong with the creation of your account: ({})", e),
            }
            Ok(())
        }
        Command::Login { email, password }=>{
            match user::login(&email, &password) {
                Ok(body) =>{
                    let parsed: serde_json::Value = serde_json::from_str(&body).map_err(|_| "Failed to parse login response")?;
                    let api_key = parsed["api_key"].as_str().ok_or("Missing api_key in response")?.to_string();
                    println!("Api key generated: {:?}", api_key);
                    println!("(always store API KEY, in case of emergency)")
                },
                Err(e) => println!("Something went wrong with your request to login to your account: ({})", e),
            }
            Ok(())
        }
        Command::DeclareGeoJson { path }=>{
            match user::declare_geojson(&path) {
                Ok(_body) =>{
                    println!("GeoJson declared in our Database: {}", path)
                },
                Err(e) => println!("Something went wrong make sure you are logged in an have the API key: ({})", e),
            }
            Ok(())
        }
        Command::History {csv} => {
            match user::get_history(&csv) {
                Ok(_body) => {
                    return Ok(())
                },
                Err(e) => println!("Something went wrong fetching your history: ({})", e),
            }
            Ok(())
        }
        Command::CsvPath { path } => {
            match user::save_csv_path_to_config(&path) {
                Ok(_) => {return Ok(())},
                Err(e) => println!("Error: {}", e),
            }
            Ok(())
        }
        Command::Info {}=>{
            match user::get_creds(){
                Ok(body) =>{
                    println!("Email:        {}", body.email);
                    println!("API key:      {}", body.api_key);
                    println!("GeoJSON path: {}", body.geojson_path);
                },
                Err(e) => println!("Something went wrong make sure you are logged in an have the API key: ({})", e),
            }
            Ok(())
        }
        Command::Init {}=>{
            let mut dir = dirs::home_dir().expect("Could not find home directory");
            dir.push(".hellascube");
            let config_file = dir.join("hc_config.toml");
            if config_file.exists() {
                println!("HellasCube is already initialized.");
                return Ok(());
            }
            fs::create_dir_all(&dir)
                .map_err(|_| "Failed to create config directory")?;
            let default_config = Config::default();
            let toml_str = toml::to_string(&default_config)
                .map_err(|_| "Failed to serialize config")?;
            fs::write(&config_file, toml_str)
                .map_err(|_| "Failed to write config file")?;
            println!("Initialized HellasCube at ~/.hellascube/hc_config.toml");
            Ok(())
        }
        Command::Ndvi{default,area, from, till, hls, landsat, csv}=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;  //getting the api key that is saved in the .toml local file for in the .hellascube
                ndi::run("http://localhost:3000/ndvi", Some("".to_string()),&from, &till, "NDVI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDVI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Ndci {default,area, from, till, hls, csv}=>{
            let source = get_hls_source(hls);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndci", Some("".to_string()),&from, &till, "NDCI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndci", Some(area), &from, &till,"NDCI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Ndti { default,area, from, till, hls, landsat, csv}=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndti", Some("".to_string()),&from, &till, "NDTI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndti", Some(area), &from, &till,"NDTI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Wofs { default,area, from, till, csv}=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/wofs", Some("".to_string()),&from, &till, "WOFS","DEFAULT",Some(api_key), "", &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/wofs", Some(area), &from, &till,"WOFS","TARGET",Some("".to_string()), "", &csv)
            }
        }
        Command::Ndwi { default,area, from, till, hls, landsat , csv}=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndwi", Some("".to_string()),&from, &till, "NDWI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndwi", Some(area), &from, &till,"NDWI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Ndmi { default,area, from, till, hls, landsat , csv}=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndmi", Some("".to_string()),&from, &till, "NDMI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndmi", Some(area), &from, &till,"NDMI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Ndbi { default,area, from, till, hls, landsat, csv }=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndbi", Some("".to_string()),&from, &till, "NDBI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndbi", Some(area), &from, &till,"NDBI","TARGET",Some("".to_string()), &source, &csv)
            }
        }
        Command::Ndsi { default,area, from, till, hls, landsat , csv}=>{
            let source = get_dataset_source(hls, landsat);
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndsi", Some("".to_string()),&from, &till, "NDSI","DEFAULT",Some(api_key), &source, &csv)
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndsi", Some(area), &from, &till,"NDSI","TARGET",Some("".to_string()), &source, &csv)
            }
        } 
    }
}

fn get_dataset_source(hls: bool, landsat: bool) -> &'static str {
    match (hls, landsat) {
        (true, _) => "hls",
        (false, true) => "landsat",
        (false, false) => "sentinel",
    }
}

fn get_hls_source(hls: bool) -> &'static str {
    if hls {
        "hls"
    } else {
        "sentinel"
    }
}