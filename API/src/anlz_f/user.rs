use crate::anlz_f::requests::{UserData};

use sqlx::Pool;
use sqlx::Postgres;
use uuid::Uuid;
//json things
use serde_json::Value;
use serde_json::json;
use axum::{extract::{Json, State}, http::StatusCode};
//for db
use sqlx::PgPool;
use sqlx::Row;
//for hashing
use argon2::{Argon2, PasswordVerifier};
use argon2::password_hash::PasswordHash;
use rand_core::OsRng;
//for the api key
use rand::Rng;
//use crate::anlz_f::db_conn::ping_database;

pub async fn cacc(State(pool): State<PgPool>,Json(payload):Json<UserData>)-> Result<Json<Value>, StatusCode>{
    println!("Strugglng to create a damn account");
    let user_id = Uuid::new_v4();
    let query="INSERT INTO users (user_id, password, declared_geo_json, email) VALUES ($1, $2, NULL ,$3)";
    //let pool=ping_database().await.map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let result=sqlx::query(query)
    .bind(user_id)
    .bind(&payload.password)
    .bind(&payload.email)//SECURITY FIX THIS HASHING IT WITH ARGON2
    .execute(&pool)
    .await;
    match result {
        Ok(r) => println!("Rows affected: {}", r.rows_affected()),
        Err(e) => println!("Query failed: {}", e)
    }
    Ok(Json(json!({ "user_id": user_id })))
}

pub async fn login(State(pool): State<PgPool>,Json(payload):Json<UserData>)-> Result<Json<Value>, StatusCode>{
    let mut api_key:String="INVALID".to_string();
    match check_cred(pool.clone(),&payload.email, &payload.password).await {
        Ok(user_id) =>{
            api_key=gen_api_key();
            let query="INSERT INTO api_k (api_key, user_id) VALUES ($1, $2)";
            let result=sqlx::query(query)
            .bind(&api_key)
            .bind(user_id)
            .execute(&pool)
            .await;
            match result {
                Ok(r) => println!("Rows affected: {}", r.rows_affected()),
                Err(e) => println!("Query failed: {}", e)
            }
        },
        Err(e) => println!("Something went wrong with your request to login to your account: ({})", e)
    }
    Ok(Json(json!({"api_key": &api_key})))
}

pub async fn check_cred(pool: Pool<Postgres>,email: &str, password: &str)-> Result<String, &'static str>{
//checking for the credentials of the user
//RETURN USERID FROM CHECK SO THAT WE CAN UPDATE THE 
    let query="SELECT user_id, password FROM users WHERE email=$1";
    let result=sqlx::query(query)
    .bind(&email)
    .fetch_one(&pool)
    .await
    .map_err(|_| "User_not_found")?;
    let stored_hash: String = result.try_get("password")
        .map_err(|_| "Failed to get password")?;
    println!("Stored hash: {}", stored_hash);
    let parsed_hash = PasswordHash::new(&stored_hash)
        .map_err(|_| "Invalid hash")?;
    Argon2::default()
        .verify_password(password.as_bytes(), &parsed_hash)
        .map_err(|_| "Wrong password")?;
    let user_id: String = result.try_get("user_id")
        .map_err(|_| "Failed to get user_id")?;
    Ok(user_id)
}

pub fn gen_api_key()-> String{
    let key: String = rand::thread_rng()
    .sample_iter(&rand::distributions::Alphanumeric)
    .take(48)
    .map(char::from)
    .collect();
    format!("hc_{}", key)
}

pub async fn declared_geo_json(){
    //we will need the api_key and 
}

pub async fn check_api(){
    //checking if api is valid and is it valid (24 hout expiration)
}
/* 
pub fn hash(hash_object: &str)-> String{
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    argon2.hash_password(hash_object.as_bytes(), &salt)
    .unwrap()
    .to_string()
}
*/

/*
THE RIGHT WAY/ NOT POSSIBLE FOR NOW BECAUSE OF PERMISSIONS...PROJECT CANT COMPILE WITH THE PERMISSIONS OF THE USB STICK
    sqlx::query!(
        "INSERT INTO users (user_id, email, password) VALUES ($1, $2, $3)",
        user_id,
        payload.email,
        payload.password
        //EXPLAIN ERROR HERE AND FUTURE FIX THIS 
        //WHEN YOU INSTALL THE VPS DON'T BIND THEM 
        //BECAUSE THEM YOU CAN ACTUALLY BUILD THEM
        //BINDING IT THE WAY TO GO WIHTOUT BUILDING 
        //for now...... 
    )
*/