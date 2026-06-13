use crate::anlz_f::requests::{UserData, GeoJsonREQ};
//use axum::body;
use sqlx::Pool;
use sqlx::Postgres;
//use sqlx::query;
use uuid::Uuid;
//json things
use serde_json::Value;
use serde_json::json;
use axum::{extract::{Json, State}, http::StatusCode}; //
//for db
use sqlx::PgPool;
use sqlx::Row;
//for the password hasher
use argon2::{Argon2, PasswordVerifier};
use argon2::password_hash::PasswordHash;
//use rand_core::OsRng;
//for api hashing
use sha2::{Sha256, Digest};
//for the api key
use rand::Rng;
use crate::anlz_f::requests::StatusReporter;
//use crate::anlz_f::db_conn::ping_database;

pub async fn cacc(pool: PgPool,reporter: StatusReporter,Json(payload):Json<UserData>)-> Result<Json<Value>, StatusCode>{
    reporter.update("PROCESSING: Account creation", None,None,None,None).await;
    let user_id = Uuid::new_v4();
    let query="INSERT INTO users (user_id, password, declared_geo_json, email) VALUES ($1, $2, NULL ,$3)";
    //let pool=ping_database().await.map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let result=sqlx::query(query)
    .bind(user_id)
    .bind(&payload.password)
    .bind(&payload.email)   //SECURITY FIX THIS HASHING IT WITH ARGON2 or not?
    .execute(&pool)
    .await;
    match result {
        Ok(r) => {
            reporter.update("DONE: Account created", None,None,None,None).await;
            println!("Rows affected: {}", r.rows_affected())
        },
        Err(e) => {
            reporter.update("FAILED: Query failed", None,None,None,None).await;
            println!("Query failed: {}", e)
        }
    }
    Ok(Json(json!({ "user_id": user_id })))
}

pub async fn login(pool: PgPool,reporter: StatusReporter,Json(payload):Json<UserData>)-> Result<Json<Value>, StatusCode>{
    //TO DO CHECK THE LOGGIN
    //MAYBE THE LOG OUT 
    reporter.update("PROCESSING: Login", None,None,None,None).await;
    let mut api_key:String="INVALID".to_string();
    match check_cred(pool.clone(),&payload.email, &payload.password).await {
        Ok(user_id) =>{
            api_key=gen_api_key();
            let query="INSERT INTO api_k (api_key, exp_date, user_id) VALUES ($1, NOW() + INTERVAL '8 hours', $2)";
            let result=sqlx::query(query)
            .bind(api_key_hash(&api_key))
            .bind(user_id)
            .execute(&pool)
            .await;
            match result {
                Ok(r) => {
                    reporter.update("DONE: user logged in", None,None,None,None).await;
                    println!("Rows affected: {}", r.rows_affected())
                },
                Err(e) =>{
                    reporter.update("FAILED: Query failure", None,None,None,None).await;
                    println!("Query failed: {}", e)
                } 
            }
        },
        Err(e) => {
            reporter.update("FAILED: Authorization failure", None,None,None,None).await;
            println!("Something went wrong with your request to login to your account: ({})", e)
        }
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

pub async fn initialize_geo_json(pool: PgPool,reporter: StatusReporter,Json(payload): Json<GeoJsonREQ>) -> Result<String, &'static str> {
    reporter.update("PROCESSING: GeoJson", None,None,None,None).await;
    let api_key = payload.api_key;
    match check_api(&pool,&api_key).await {
        Ok(user_id) => {
            let query="UPDATE users SET declared_geo_json = $1::json WHERE user_id = $2;";
            let result=sqlx::query(query)
            .bind(payload.geo_json)
            .bind(user_id)
            .execute(&pool)
            .await;
            match result {
                Ok(r) => {
                    reporter.update("DONE: GeoJson initialized", None,None,None,None).await;
                    println!("Rows affected: {}", r.rows_affected())
                },
                Err(e) => {
                    reporter.update("FAILED: Query failed", None,None,None,None).await;
                    println!("Query failed: {}", e)
                }
            }
            Ok("SUCESS".to_string())
        }
        Err(_e) => {
            reporter.update("FAILED: Invalid API key", None, None, None, None).await;
            println!("API_KEY DID NOT WORK");
            Err("API DID NOT WORK")}
    }
}

pub async fn check_api(pool: &Pool<Postgres>,api_key: &str) -> Result<String, &'static str> {
    let hashed_api_key=api_key_hash(api_key);
    let query="SELECT user_id FROM api_k WHERE api_key=$1 AND is_active=true";
    let result=sqlx::query(query)
    .bind(hashed_api_key)
    .fetch_one(pool)
    .await
    .map_err(|_| "API_KEY_NOT_FOUND")?;
    let user_id=result.try_get("user_id").map_err(|_| "Failed to get user_id")?;
    println!("User_id:  {}", user_id);
    Ok(user_id)
}

fn api_key_hash(hash_object: &str) -> String {
    //we are using a diffrent hasher for the api_keys a faster and better way for the api keys SHA 256
    let mut hasher = Sha256::new();
    hasher.update(hash_object.as_bytes());
    hex::encode(hasher.finalize())
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