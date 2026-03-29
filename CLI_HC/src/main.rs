//use std::env;
//use std::fs;
use std ::process;
use clap::Parser;


#[derive(Parser)]
struct Args {
    #[arg(short = 'n', long = "name")]
    name: Option<String>,

    #[arg(short = 'c', long = "city")]
    city: Option<String>,

    #[arg(short = 'f', long = "from")]
    from: Option<String>,

    #[arg(short = 't', long = "till")]
    till: Option<String>,
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
        match (&args.name, &args.city, &args.from, &args.till) {
            (Some(n), Some(c), None, None) => {
                println!("Hello {}, from {}!", n, c);
                //calling function sending flags to server 
                Ok(())
            }
            (None, Some(c), Some(f), Some(t)) => {
                println!("City: {}, From: {} Till: {}", c, f, t);
                Ok(())
            }
            _ => {
                Err("Invalid combination of arguments!")
            }
            /*  waiting for response
                getting response
                printing response....or
            */
        }
    }
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