use crate::http::get_no_data;

pub fn run()-> Result<(), &'static str>{
    //i am using functions i created in http.rs
    let res= get_no_data("http://localhost:3000/api");
    match res {
        Ok(body) => println!("{}",body),
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}