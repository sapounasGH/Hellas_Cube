pub mod stark;
pub mod help;
pub mod ndi;
pub mod declare_geojson;
pub mod user;
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
            ndi::run("http://localhost:3000/ndvi",&area, &from, &till)
        }
        Command::Ndci { area, from, till }=>{
            ndi::run("http://localhost:3000/ndci",&area, &from, &till)
        }
        Command::Ndti { area, from, till }=>{
            ndi::run("http://localhost:3000/ndti",&area, &from, &till)
        }
        Command::Wofs { area, from, till }=>{
            ndi::run("http://localhost:3000/wofs",&area, &from, &till)
        }
        Command::Sdd { area, from, till }=>{
            ndi::run("http://localhost:3000/sdd",&area, &from, &till)
        }
        Command::Ndwi { area, from, till }=>{
            ndi::run("http://localhost:3000/ndwi",&area, &from, &till)
        }
        Command::Ndmi { area, from, till }=>{
            ndi::run("http://localhost:3000/ndmi",&area, &from, &till)
        }
        Command::Ndbi { area, from, till }=>{
            ndi::run("http://localhost:3000/ndbi",&area, &from, &till)
        }
        Command::Ndsi { area, from, till }=>{
            ndi::run("http://localhost:3000/ndsi",&area, &from, &till)
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