use clap::{Parser, Subcommand};

#[derive(Parser)] 
#[command(author, version, about, long_about = None)]
pub struct Args {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand)]
pub enum Command {
    Ndvi{
        #[arg(long)]
        city: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
    },
    Stark{},
}