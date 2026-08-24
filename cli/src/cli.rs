use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
// TODO I HAVE TO ADD PARSING ON THE COMMANDS SO THAT THE USER DOESNT PASS ENYTHING WE WANTS
#[derive(Parser)]
#[command(disable_help_subcommand = true)] 
#[command(author, version, about, long_about = None)]
pub struct Args {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct Config {
    pub email: String,
    pub api_key: String,
    pub geojson_path: String,
    pub csv_path: String
}

impl Config {
    pub fn set_creds(mut self, email: String, api_key: String) -> Self {
        self.email = email;
        self.api_key = api_key;
        self
    }
    
    pub fn save_gj_path(mut self, path: String) -> Self {
        self.geojson_path = path;
        self
    }

    pub fn save_csv_path(mut self, path: String) -> Self {
        self.csv_path = path; 
        self
    }
}

#[derive(Subcommand)]
pub enum Command {
    Help{},
    DeclareGeoJson{
        #[arg(long)]
        path: String
    },
    Info{},
    Init{},
    Cacc{
        #[arg(long)]
        email: String,
        #[arg(long)]
        password: String
    },
    Login{
        #[arg(long)]
        email: String,
        #[arg(long)]
        password: String
    },
    History{
        #[arg(long)]
        csv: bool,
    },
    CsvPath{
        #[arg(long)]
        path: String,
    },
    Ndvi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndci{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long)]
        hls: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndti{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndwi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndmi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String, 
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndbi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndsi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long, conflicts_with = "landsat")]
        hls: bool,
        #[arg(long, conflicts_with = "hls")]
        landsat: bool,
        #[arg(long)]
        csv: bool,
    },
    Wofs{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default",value_parser = validate_area)]
        area: Option<String>,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
        #[arg(long)]
        csv: bool,
    }
}

//Parsing the iputs functions
fn validate_area(s: &str) -> Result<String, clap::Error> {
    let reserved = ["null", "none", "all"];
    
    if reserved.contains(&s.to_lowercase().as_str()) {
        Err(clap::Error::raw(
            clap::error::ErrorKind::InvalidValue,
            format!("'{}' is not a valid area name\n", s)
        ))
    } else {
        Ok(s.to_string())
    }
}