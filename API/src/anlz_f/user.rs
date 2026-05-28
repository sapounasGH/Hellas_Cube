use crate::anlz_f::requests::{UserData};
use axum::{extract::Json, extract::State, http::StatusCode,};
use reqwest::Client;
use serde_json::Value;
use sqlx::PgPool;
use uuid::Uuid;

pub async fn cacc(State(pool): State<PgPool>,Json(payload): Json<UserData>)-> Result<(), StatusCode>{
    //creating account
    println!("Strugglng to create a damn account");
    let user_id = Uuid::new_v4();
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
    .execute(&pool)
    .await?;
    Ok(())
}