use crate::http::send;

pub fn run(area: &str, from: &str, till: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    { //stelnoume ta dedomena
        "city": area,
        "from": from,
        "till": till
    });
        let res= send("http://localhost:3000/sdd", json);
        match res {
            Ok(body) => println!("RESULTS: {}",body),
            Err(e)   => println!("Error: {}", e),
        }
        Ok(())
}