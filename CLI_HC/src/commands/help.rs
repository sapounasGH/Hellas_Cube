pub fn run()-> Result<(), &'static str>{
    println!("{}",HELP_TEXT);
    Ok(())
}

const HELP_TEXT: &str = "
╔══════════════════════════════════════════════════════╗
║              Hellas Cube CLI                         ║
╚══════════════════════════════════════════════════════╝

USAGE:
    hellas-cube <COMMAND> [OPTIONS]

COMMANDS:
    ndvi       Compute Normalized Difference Vegetation Index (NDVI) for a municipality/lake/river etc
    ndci       Compute Normalized Difference Chlorofyll Index (NDVI) for a municipality/lake/river etc
    ndti       Compute Normalized Difference Turbidity Index (NDVI) for a municipality/lake/river etc
    wofs       Find the percentage of of water in an area using WOFS algorythm
    help       Show this help message

OPTIONS:
    --municipality   Name of the municipality   (e.g. Municipality of Athens)
    --from           Start date                 (e.g. 10-12-2020)
    --to             End date                   (e.g. 20-12-2020)

EXAMPLES:
    hellas-cube ndvi --city Thassos Municipality --from 10-12-2020 --to 20-12-2020
    hellas-cube wofs  --city Municipality of Thessaloniki --from 10-12-2020 --to 20-12-2020
";