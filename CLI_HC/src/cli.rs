use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(disable_help_subcommand = true)] 
#[command(author, version, about, long_about = None)]
pub struct Args {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand)]
pub enum Command {
    Help{},
    Stark{},
    DeclareGeoJson{
        path: String
    },
    Info{},
    Ndvi{
        /*#[arg(long, conflicts_with = "area")]
        default: bool,
        #[arg(long, conflicts_with = "default")]
        area: Option<String>,*/
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
    },
    Ndci{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
    },
    Ndti{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,
    },
    Ndwi{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String, 
    },
    Ndmi{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String, 
    },
    Ndbi{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String, 
    },
    Ndsi{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String, 
    },
    Wofs{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,  
    },
    Sdd{
        #[arg(long)]
        area: String,
        #[arg(long)]
        from: String,
        #[arg(long)]
        till: String,  
    }
}