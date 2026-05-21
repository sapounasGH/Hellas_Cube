use std::{fs, path::PathBuf};

fn config_path() -> PathBuf {
    let mut path = dirs::home_dir().expect("Could not find home directory");
    path.push(".hellascube");
    fs::create_dir_all(&path).ok();
    path.push("declare_geojson.toml");
    path
}

pub fn save_geojson_path(geojson_path: &str) -> Result<(), &'static str> {
    fs::write(config_path(), geojson_path).map_err(|_| "Failed to save config")
}

pub fn load_geojson_path() -> Result<String, &'static str> {
    let content = fs::read_to_string(config_path())
        .map_err(|_| "No declared GeoJSON found. Run `declare-geojson` first.")?;
    Ok(content.trim().to_string())
}
/* 
pub fn load_geojson_file() -> Result<String, &'static str> {
    let path = load_geojson_path()?;
    
    fs::read_to_string(&path)
        .map_err(|_| "Could not read the declared GeoJSON file. Does it still exist at that path?")
}*/