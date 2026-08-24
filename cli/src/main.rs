#[macro_use]
extern crate prettytable;

mod commands;
mod cli;
mod http;
mod export;
mod export_to_csv;
use clap::Parser;
use cli::Args;

//Main function.....DONT OVERLOAD IT !!!!!
fn main() {
    let args = Args::parse();
    if let Err(e) = commands::matching(args) {
        eprintln!("PROBLEMO: {}", e);
        std::process::exit(1);
    }
}