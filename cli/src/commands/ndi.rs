use crate::http::send;
use crate::export::export;
use crate::export_to_csv::export_to_csv;

pub fn run(path: &str, area: Option<String>, from: &str, till: &str, index: &str, req_type: &str, api_key: Option<String>, source: &str, csv: &bool) -> Result<(), &'static str> {
    let json = &serde_json::json!({   
        "index": index,
        "req_type": req_type,
        "api_key": api_key,
        "city": area,
        "from": from,
        "till": till,
        "source": source
    });
    
    let res = send(path, json);
    
    match res {
        Ok(body) => {
            export(&body);
            if *csv {
                match export_to_csv(&body) {
                    Ok(_) => println!("Successfully appended to CSV"),
                    Err(e) => println!("CSV Error: {}", e),
                }
            }
            
            Ok(())
        },
        Err(e) => {
            println!("Error: {}", e);
            Err("Failed to execute request")
        }
    }
}