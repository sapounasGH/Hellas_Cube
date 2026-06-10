use crate::http::send;
use argon2::{Argon2, PasswordHasher};
use argon2::password_hash::SaltString;
use rand_core::OsRng;
use crate::cli::Config;
use std::{fs};  //, path::PathBuf
use toml;

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
    let res= send("http://localhost:3000/declare_geojson", json);  //build the api
    match res{
        Ok(body)=>{
            let _=save_path_to_config(geojson_path);    //last command is saving it to the .toml file 
            Ok(body)
        }
        Err(_e) => Err("Error declaring geojson, check API KEY.")
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
//get api_key so that we can take it on each request
pub fn get_api_key()-> Result<String, &'static str>{
    /*    //function to reead credentials of the user
    //fs::write(config_path(), geojson_path).map_err(|_| "Failed to save config");
    let config_file = dirs::home_dir().expect("Could not find home directory").join(".hellascube").join("hc_config.toml");
    let existing = fs::read_to_string(&config_file).map_err(|_| "Failed to read config")?;
    let config: Config = toml::from_str(&existing).map_err(|_| "Failed to parse config")?;
    let contents = fs::read_to_string(geojson_path).expect("Should have been able to read the file"); */
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


/*TRASH
/no point in this current one it is clearly pure testing function
pub fn load_geojson_path() -> Result<String, &'static str> {
    let content = fs::read_to_string(config_path())
        .map_err(|_| "No declared GeoJSON found. Run `declare-geojson` first.")?;
    println!("{}",content.trim().to_string());
    Ok(content.trim().to_string())
}

//saving credentials
pub fn save_creds(){

}

*/