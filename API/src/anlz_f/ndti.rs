use crate::anlz_f::requests::{IndexRequest};
use axum::{
    extract::Json,
    http::StatusCode,
};
use reqwest::Client;
use serde_json::Value;

pub async fn run(Json(payload):Json<IndexRequest>)-> Result<Json<Value>, StatusCode>{
    //calling python
    let to_send: serde_json::Value = serde_json::json!({
    "place": payload.city,
    "index": "NDVI",
    "date1": payload.from,
    "date2": payload.till
    });
    let client = Client::new();
    let response = client
        .post("http://localhost:8080/analyzation/ndti")
        .json(&to_send)
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let resp = response
            .json::<Value>()
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(resp))
}