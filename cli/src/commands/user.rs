use crate::http::send;
use crate::export::export;
use crate::cli::Config;
use crate::export_to_csv::export_to_csv;
use std::{fs};
use toml;

//for hashing
use argon2::{Argon2, PasswordHasher};
use argon2::password_hash::SaltString;
use rand_core::OsRng;

pub fn cacc(email: &str, password: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {   
        "email": email,
        "password": hash(password)
    });
    let res= send("http://localhost:3000/cacc", json);
    match res {
        Ok(body) => println!("User-id: {}", body),
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}

pub fn login(email: &str, password: &str)->Result<String, &'static str>{
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    if !config_file.exists() {
        return Ok("HellasCube is not initialized. Run `hellascube init` first.".to_string());
    }
    let json= &serde_json::json!(
    {   
        "email": email,
        "password": password
    });
    let res= send("http://localhost:3000/login", json);
    match res {
        Ok(body) =>{
            let parsed: serde_json::Value = serde_json::from_str(&body).map_err(|_| "Failed to parse response")?;
            let api_key = parsed["api_key"].as_str().ok_or("Missing api_key")?;
            let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
            let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
            let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
            let updated = config.set_creds(email.to_string(), api_key.to_string());
            let toml_str = toml::to_string(&updated).map_err(|_| "Failed to serialize config")?;
            fs::write(&config_file, toml_str).map_err(|_| "Failed to write config")?;
            println!("Credentials saved.");
            Ok(body)
        },
        Err(_e)   => Err("error on login"),
    }
}

pub fn declare_geojson(geojson_path: &str) -> Result<String, &'static str>{
    let contents = fs::read_to_string(geojson_path).expect("Should have been able to read the file");
    let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
    //send to 
    let json= &serde_json::json!(
    {   
        "api_key": api_key,
        "geo_json": contents
    });
    let res= send("http://localhost:3000/declare_geojson", json);  //build the api request
    match res{
        Ok(body)=>{
            let _=save_path_to_config(geojson_path);    //last command is saving it to the .toml file 
            Ok(body)
        }
        Err(_e) => Err("Error declaring geojson, check API KEY.")
    }
}

pub fn get_history(csv: &bool) -> Result<(), &'static str> {
    let api_key = get_api_key().map_err(|_| "Failed to get API key")?;
    
    let json = &serde_json::json!({
        "api_key": api_key
    });
    
    let res = send("http://localhost:3000/history", json);
    match res {
        Ok(body) => {
            export(&body);
            if *csv {
                match crate::export_to_csv::export_to_csv(&body, None) {
                    Ok(_) => {
                        println!("Successfully appended to CSV");
                    },
                    Err(e) => {
                        println!("CSV Error: {}", e);
                        return Err("Failed to save CSV file");
                    }                
                }
            }
            Ok(())
        },
        Err(_) => Err("Error fetching user history, check API KEY."),
    }
}

fn save_path_to_config(path: &str)-> Result<(), &'static str>{
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
    let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
    let updated = config.save_gj_path(path.to_string());
    let toml_str = toml::to_string(&updated).map_err(|_| "Failed to serialize config")?;
    fs::write(&config_file, toml_str).map_err(|_| "Failed to write config")?;
    Ok(())
}

pub fn save_csv_path_to_config(path: &str) -> Result<(), &'static str> {
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
    let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
    
    // Use the new method we added to Config
    let updated = config.save_csv_path(path.to_string());
    
    let toml_str = toml::to_string(&updated).map_err(|_| "Failed to serialize config")?;
    fs::write(&config_file, toml_str).map_err(|_| "Failed to write config")?;
    
    println!("CSV export path saved as: {}", path);
    Ok(())
}

//get api_key so that we can take it on each request
pub fn get_api_key()-> Result<String, &'static str>{
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
    let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
    Ok(config.api_key)
}

pub fn get_creds()-> Result<Config, &'static str>{
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
    let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
    Ok(config)
}

fn hash(hash_object: &str) -> String {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    argon2.hash_password(hash_object.as_bytes(), &salt)
        .unwrap()
        .to_string()
}