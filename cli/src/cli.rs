use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

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

fn validate_path(s: &str) -> Result<String, String> {
    let path = PathBuf::from(s);
    if !path.exists() {
        return Err(format!("Path does not exist: {}", s));
    }
    Ok(s.to_string())
}

fn parse_date(s: &str) -> Result<String, String> {
    if s.len() != 10 || s.chars().nth(2) != Some('-') || s.chars().nth(5) != Some('-') {
        return Err("Date must be DD-MM-YYYY".to_string());
    }
    let day: u32 = s[0..2].parse().map_err(|_| "Invalid day".to_string())?;
    let month: u32 = s[3..5].parse().map_err(|_| "Invalid month".to_string())?;
    let year: i32 = s[6..10].parse().map_err(|_| "Invalid year".to_string())?;
    if month < 1 || month > 12 {
        return Err("Month must be 01-12".to_string());
    }
    if day < 1 || day > 31 {
        return Err("Day must be 01-31".to_string());
    }
    if day > 30 && (month == 4 || month == 6 || month == 9 || month == 11) {
        return Err("Month has only 30 days".to_string());
    }
    if month == 2 {
        let leap = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
        let max_day = if leap { 29 } else { 28 };
        if day > max_day {
            return Err(format!("February has {} days in {}", max_day, year));
        }
    }
    Ok(s.to_string())
}

fn parse_email(s: &str) -> Result<String, String> {
    if s.is_empty() {
        return Err("Email cannot be empty".to_string());
    }
    if !s.contains('@') {
        return Err("Email must contain @".to_string());
    }
    let parts: Vec<&str> = s.split('@').collect();
    if parts.len() != 2 {
        return Err("Email must contain exactly one @".to_string());
    }
    if parts[0].is_empty() {
        return Err("Email local part cannot be empty".to_string());
    }
    if !parts[1].contains('.') {
        return Err("Email domain must contain a dot".to_string());
    }
    if parts[1].starts_with('.') || parts[1].ends_with('.') || parts[1].contains("..") {
        return Err("Email domain is invalid".to_string());
    }
    Ok(s.to_string())
}

#[derive(Subcommand)]
pub enum Command {
    Help{},
    DeclareGeoJson{
        #[arg(long, value_parser = validate_path)]
        path: String
    },
    Info{},
    Init{},
    History{
        #[arg(long)]
        csv: bool,
    },
    CsvPath{
        #[arg(long, value_parser = validate_path)]
        path: String,
    },
    Login{
        #[arg(long, value_parser = parse_email)]
        email: String,
        #[arg(long)]
        password: String
    },
    Cacc{
        #[arg(long, value_parser = parse_email)]
        email: String,
        #[arg(long)]
        password: String
    },
    Ndvi{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
        till: String,
        #[arg(long)]
        hls: bool,
        #[arg(long)]
        csv: bool,
    },
    Ndti{
        #[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
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
        #[arg(long, conflicts_with = "default", value_parser = validate_area)]
        area: Option<String>,
        #[arg(long, value_parser = parse_date)]
        from: String,
        #[arg(long, value_parser = parse_date)]
        till: String,
        #[arg(long)]
        csv: bool,
    }
}