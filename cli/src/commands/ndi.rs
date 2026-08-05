use crate::http::send;

pub fn run(path: &str,area: Option<String>, from: &str, till: &str, index: &str,req_type: &str, api_key: Option<String>)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {   
        "index": index,
        "req_type": req_type,
        "api_key": api_key,
        "city": area,
        "from": from,
        "till": till
    });
    let res= send(path, json);
    match res {
        Ok(body) => {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(&body) {
                println!("\n── HellasCube Results ──────────────────");
                if let Some(status) = json.get("STATUS") {
                    println!("  Status    : {}", status.as_str().unwrap_or("-"));
                }
                if let Some(index) = json.get("analyzation") {
                    println!("  Index     : {}", index.as_str().unwrap_or("-"));
                }
                if let Some(place) = json.get("place") {
                    println!("  Area      : {}", place.as_str().unwrap_or("-"));
                }
                if let Some(time) = json.get("time") {
                    println!("  Time      : {}", time.as_str().unwrap_or("-"));
                }
                if let Some(result) = json.get("result") {
                    println!("  ────────────────────────────────────");
                    if let Some(obj) = result.as_object() {
                        for (k, v) in obj {
                            println!("  {:8} : {}", k, v);
                        }
                    }
                }
                println!("────────────────────────────────────────\n");
            } else {
                println!("RESULTS: {}", body);
            }
        },
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}