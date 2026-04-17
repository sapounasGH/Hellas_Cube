use serde_json::Value;

pub fn send(url: &str, data: &Value)-> Result<String, Box<dyn std::error::Error>>{                
    let client = reqwest::blocking::Client::builder().timeout(None).build().map_err(|_| "Failed to build client")?;
    let response = client
    .post(url)  
    .json(&data)
    .send()
    .map_err(|e| {eprintln!("Failed to reach server: {:?}", e);e})?;
    let body = response.text().map_err(|e| {eprintln!("Failed to get response: {:?}", e);e})?;
    //println!("{}", body);
    Ok(body)
}