pub mod ndvi;
pub mod stark;

use crate::cli::{Args, Command};

pub fn matching(args: Args)-> Result<(), &'static str>{
        match args.command{
            Command::Stark {}=>{
                stark::run();
                Ok(())
            }
            Command::Ndvi{city, from, till}=>{
                ndvi::run(&city, &from, &till)
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