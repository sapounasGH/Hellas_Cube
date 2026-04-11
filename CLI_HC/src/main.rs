//use std::env;
//use std::fs;
use std::process;
use clap::{Command, Parser};
use serde_json::Value;
//use reqwest::Url;

/* 

#[derive(Parser)]
struct Args {
    #[arg(short = 'c', long = "city")]
    city: Option<String>,

    #[arg(short = 'f', long = "from")]
    from: Option<String>,

    #[arg(short = 't', long = "till")]
    till: Option<String>,

    #[arg(long = "ndvi", default_value_t=false)]
    ndvi: bool
}
*/
enum Command {
    Ndvi{
        #[arg(long)]
        city: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
    }
}

//ping server

//Main function.....DONT OVERLOAD IT !!!!!
fn main() {
    let args = Args::parse();
    Args::matching(args).unwrap_or_else(|err:&str|{
        println!("Problemo: {}", err);
        process::exit(1);
    });
}

//get data from commands etc.
impl Args{
    fn matching(args: Args)-> Result<(), &'static str>{
        let args= Args::parse();

        match args.command{
            Command::stark {None}=>{
                println!("You know N0thing Jon Snow!");
                Ok(())
            }
            Command::Ndvi{city, from, till}=>{
                let json= &serde_json::json!(
                { //stelnoume ta dedomena
                    "city": city,
                    "from": from,
                    "till": till
                });
                let res= send("http://localhost:3000/ndvi", json);
                println!("The ndvi for for {} from {} till {} is {}",city, from, till, res);
                Ok(())
            }
            _ => {
                Err("Invalid Combination bro....<3")
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
    }
}

fn send(url: &str, data: &Value)-> Result<&'static str, Box<dyn std::error::Error>>{                
    let client = reqwest::blocking::Client::builder().timeout(None).build().map_err(|_| "Failed to build client")?;
    let response = client
    .post(url)  
    .json(&data)
    .send()
    .map_err(|e| {eprintln!("Failed to reach server: {:?}", e);e})?;
    /*
    FIX ERROR SEE WHY WE CAN SEE THE ERROR
    we cant reach server but the curling with postman works...
    Failed to reach server: reqwest::Error { kind: Request, url: "http://localhost:3000/ndvi", source: TimedOut }
    need to remove timeout....the analyzation needs time
    */
    let body = response.text()
                                .map_err(|e| {eprintln!("Failed to get response: {:?}", e);e})?;
    println!("{}", body);
    Ok(&body)
}
/*Function sending the flags and data to the server
fn sendData(args.data){

}
*/


/*
use std::process;
use clap::{Parser, Subcommand};

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Greet { name, city } => {
            println!("Hello {}, from {}!", name, city);
        }
        Commands::Travel { from, till } => {
            println!("Travelling from {} to {}!", from, till);
        }
    }
}

#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Greet {
        #[arg(short = 'n', long = "name")]
        name: String,

        #[arg(short = 'c', long = "city")]
        city: String,
    },
    Travel {
        #[arg(short = 'f', long = "from")]
        from: String,

        #[arg(short = 't', long = "till")]
        till: String,
   
*/