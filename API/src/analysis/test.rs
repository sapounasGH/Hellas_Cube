use axum::{
    extract::Json,
    http::StatusCode,
};
use reqwest::Client;
use serde_json::Value;

pub async fn run()-> Result<Json<Value>, StatusCode>{
    let client = Client::new();
    println!("GOOD FROM RUSTY API");
    let response = client
        .get("http://localhost:8080/test")
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let resp = response
            .json::<Value>()
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(resp))
}