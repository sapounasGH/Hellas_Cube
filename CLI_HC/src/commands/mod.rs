pub mod stark;
pub mod help;
pub mod ndi;
pub mod user;
use crate::cli::{Args, Command, Config};
use std::{fs};  //, path::PathBuf
use toml;
use crate::commands::user::get_api_key;
/*so we will conflict area & default have some fn for the loading of the geojson etc */
pub fn matching(args: Args)-> Result<(), &'static str>{
    match args.command{
        Command::Help {}=>{
            help::run()
        }
        Command::Stark {}=>{
            stark::run()
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
                Ok(api_key) =>{
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
        Command::Ndvi{default,area, from, till}=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;  //getting the api key that is saved in the .toml local file for in the .hellascube
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDVI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDVI","TARGET",None)
            }
        }
        Command::Ndci {default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDCI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDCI","TARGET",None)
            }
        }
        Command::Ndti { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDTI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDTI","TARGET",None)
            }
        }
        Command::Wofs { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "WOFS","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"WOFS","TARGET",None)
            }
        }
        Command::Sdd { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "SDD","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"SDD","TARGET",None)
            }
        }
        Command::Ndwi { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDWI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDWI","TARGET",None)
            }
        }
        Command::Ndmi { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDMI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDMI","TARGET",None)
            }
        }
        Command::Ndbi { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDBI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDBI","TARGET",None)
            }
        }
        Command::Ndsi { default,area, from, till }=>{
            if default {
                let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
                ndi::run("http://localhost:3000/ndvi", None,&from, &till, "NDSI","DEFAULT",Some(api_key))
            } else {
                let area = area.ok_or("Provide --area or use --default")?;
                ndi::run("http://localhost:3000/ndvi", Some(area), &from, &till,"NDSI","TARGET",None)
            }
        } 
    }
}

    
/* 
        match (&args.city, &args.from, &args.till, &args.ndvi) {
            (None, None, None, false) => {
                println!("You know Nothing Jon Snow");
                Ok(())
            }
            (Some(c), Some(f), Some(t), ndvi) => {
                let json= &serde_json::json!(
                { //stelnoume ta dedomena
                    "city": c,
                    "from": f,
                    "till": t
                });
                let res= send("http://localhost:3000/ndvi", json);
                println!("{}", res);
                Ok(())
            }
            _ => {
                Err("Invalid combination of arguments!")
            }
        }*/