use crate::http::send;

pub fn run(path: &str,area: Option<String>, from: &str, till: &str, req_type: &str, api_key: Option<String>)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {   
        "req_type": req_type,
        "api_key": api_key,
        "city": area,
        "from": from,
        "till": till
    });
    let res= send(path, json);
    match res {
        Ok(body) => println!("RESULTS: {}", body),
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}