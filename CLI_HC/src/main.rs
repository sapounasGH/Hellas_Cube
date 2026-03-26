//use std::env;
//use std::fs;
use std::process;
use clap::Parser;
fn main() {
    //let args: Vec<String> = env::args().collect();
    let args=Args::parse();
    let config=Config::new(args).unwrap_or_else(|err|{
        println!("Problemo: {}", err);
        process::exit(1);
    });
    println!("So my name is {}", config.myname);
    println!("And my birthday is {}", config.city);
}

struct Config{
    myname: String,
    city: String
}

impl Config {
    fn new(args: Args) -> Result<Config, &'static str>{
        if args.myname.is_empty() || args.city.is_empty() {
            return Err("You didn't give us enough arguments!");
        }
        Ok(Config { myname:args.myname, city:args.city})
    }   
}

//This is the Arguents

#[derive(Parser)]
struct Args {
    #[arg(short = 'n', long = "name")]
    myname: String,

    #[arg(short = 'c', long = "city")]
    city: String,
}