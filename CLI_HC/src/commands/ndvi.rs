use crate::http::send;

pub fn run(city: &str, from: &str, till: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    { //stelnoume ta dedomena
        "city": city,
        "from": from,
        "till": till
        });
        let res= send("http://localhost:3000/ndvi", json);
        match res {
            Ok(body) => println!("NDVI for {} from {} till {} is: {}", city, from, till, body),
            Err(e)   => println!("Error: {}", e),
        }
        Ok(())
}