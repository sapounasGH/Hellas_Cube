use crate::http::send;

pub fn cacc(email: &str, password: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {   
        "email": email,
        "password": password
    });
    let res= send("http://localhost:3000/ADDROUTETOCREATEACC", json);
    match res {
        Ok(body) => println!("User-id: {}", body),
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}

pub fn login(email: &str, password: &str)->Result<String, &'static str>{
    let api_key="RANDOMAPIKEY129836916398^^!(&$^(*";
    Ok(api_key.to_string())
}