use crate::http::send;
use argon2::{Argon2, PasswordHasher};
use argon2::password_hash::SaltString;
use rand_core::OsRng;

pub fn cacc(email: &str, password: &str)-> Result<(), &'static str>{
    let json= &serde_json::json!(
    {   
        "email": email,
        "password": hash(password)
    });
    let res= send("http://localhost:3000/cacc", json);
    match res {
        Ok(body) => println!("User-id: {}", body),
        Err(e)   => println!("Error: {}", e),
    }
    Ok(())
}

pub fn login(email: &str, password: &str)->Result<String, &'static str>{
    let json= &serde_json::json!(
    {   
        "email": email,
        "password": hash(password)
    });
    let res= send("http://localhost:3000/ADDROUTETOCREATEACC", json);
    match res {
        Ok(body) => Ok(body),
        Err(_e)   => Err("error on login"),
    }
}

fn hash(hash_object: &str) -> String {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    argon2.hash_password(hash_object.as_bytes(), &salt)
        .unwrap()
        .to_string()
}