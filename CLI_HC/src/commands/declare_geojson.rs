use std::{fs, path::PathBuf};

//maybe use this function to config things like 
fn config_path() -> PathBuf {
    let mut path = dirs::home_dir().expect("Could not find home directory");
    path.push(".hellascube");
    fs::create_dir_all(&path).ok();
    path.push("declare_geojson.toml");
    path
}

//going to make this the main function of the saving of the geojson
pub fn save_geojson_path(geojson_path: &str) -> String{
    fs::write(config_path(), geojson_path).map_err(|_| "Failed to save config");
    let contents = fs::read_to_string(geojson_path)
        .expect("Should have been able to read the file");
    contents.to_string()
    //send to 
}

//no point in this current one it is clearly pure testing function
pub fn load_geojson_path() -> Result<String, &'static str> {
    let content = fs::read_to_string(config_path())
        .map_err(|_| "No declared GeoJSON found. Run `declare-geojson` first.")?;
    println!("{}",content.trim().to_string());
    Ok(content.trim().to_string())
}
/* 
pub fn load_geojson_file() -> Result<String, &'static str> {
    let path = load_geojson_path()?;
    
    fs::read_to_string(&path)
        .map_err(|_| "Could not read the declared GeoJSON file. Does it still exist at that path?")
}*/