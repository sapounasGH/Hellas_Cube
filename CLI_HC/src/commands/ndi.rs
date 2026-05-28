use crate::http::send;

pub fn run(path: &str,area: &str, from: &str, till: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {
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