pub mod ndvi;
pub mod stark;
pub mod ndci;
pub mod ndti;
pub mod wofs;
pub mod help;
pub mod sdd;
pub mod ndwi;
pub mod ndmi;
pub mod ndbi;
pub mod ndsi;
pub mod declare_geojson;
use crate::cli::{Args, Command};

/*so we will conflict area & default have some fn for the loading of the geojson etc */
pub fn matching(args: Args)-> Result<(), &'static str>{
        match args.command{
            Command::Help {}=>{
                help::run()
            }
            Command::Stark {}=>{
                stark::run()
            }
            Command::DeclareGeoJson { path }=>{
                declare_geojson::save_geojson_path(&path)?;
                println!("GeoJson declared: {}", path);
                Ok(())
            }
            Command::Info {}=>{
                match declare_geojson::load_geojson_path() {
                    Ok(path) => println!("Declared GeoJSON: {}", path),
                    Err(e) => println!("Declared GeoJSON: Not set ({})", e),
                }
                Ok(())
            }
            Command::Ndvi{/*default,*/area, from, till}=>{
                ndvi::run(&area, &from, &till)
            }
            Command::Ndci { area, from, till }=>{
                ndci::run(&area, &from, &till)
            }
            Command::Ndti { area, from, till }=>{
                ndti::run(&area, &from, &till)
            }
            Command::Wofs { area, from, till }=>{
                wofs::run(&area, &from, &till)
            }
            Command::Sdd { area, from, till }=>{
                sdd::run(&area, &from, &till)
            }
            Command::Ndwi { area, from, till }=>{
                ndwi::run(&area, &from, &till)
            }
            Command::Ndmi { area, from, till }=>{
                ndmi::run(&area, &from, &till)
            }
            Command::Ndbi { area, from, till }=>{
                ndbi::run(&area, &from, &till)
            }
            Command::Ndsi { area, from, till }=>{
                ndsi::run(&area, &from, &till)
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