use crate::anlz_f::requests::{UserData};

use uuid::Uuid;
//json things
use serde_json::Value;
use serde_json::json;
use axum::{extract::{Json, State}};
//for db
use sqlx::PgPool;
//for hashing
use argon2::{Argon2, PasswordHasher};
use argon2::password_hash::SaltString;
use rand_core::OsRng;
//use crate::anlz_f::db_conn::ping_database;

pub async fn cacc(State(pool): State<PgPool>,Json(payload):Json<UserData>)-> Result<Json<Value>, StatusCode>{
    println!("Strugglng to create a damn account");
    let user_id = Uuid::new_v4();
    let query="INSERT INTO users (user_id, user_api_key, password, declared_geo_json, email) VALUES ($1, NULL ,$2, NULL ,$3)";
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
    println!("Login operation underway");
    match check_cred(&payload.email, &payload.password) {
        Ok(user_id) =>{
            println!("Logging in.......");
            let api_key="bruh_api_key";
            let query="UPDATE users SET user_api_key = $1 WHERE user_id = $2";
            let result=sqlx::query(query)
            .bind(api_key)
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
    Ok(Json(json!({ "api_key": api_key })))
}

pub async fn check_cred(email: &str, password: &str)-> Result<String, &'static str>{
//checking for the credentials of the user
//RETURN USERID FROM CHECK SO THAT WE CAN UPDATE THE 
    let query="SELECT user_id FROM users WHERE email=$1 AND password=$2";
    let result=sqlx::query(query)
    .bind(&email)
    .bind(&password)
    .fetch_one(&pool)
    .await
    .map_err(|_| "Invalid");
    let user_id: String = row.try_get("user_id")
        .map_err(|_| "Failed to get user_id")?;

    Ok(user_id)
}

pub async fn hash(hash_object: &str){
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    argon2.hash_password(hash_object.as_bytes(), &salt)
    .unwrap()
    .to_string();
}

pub async fn gen_api_key(){
    //generate api key
}
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