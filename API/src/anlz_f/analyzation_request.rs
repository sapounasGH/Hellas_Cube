use std::os::unix::raw::uid_t;

use crate::anlz_f::requests::{IndexRequest};
use axum::{
    extract::Json,
    http::StatusCode
};
use reqwest::Client;
use serde_json::Value;
use sqlx::PgPool;
use sqlx::Row;
use crate::anlz_f::user::check_api;
use crate::anlz_f::requests::StatusReporter;

pub async fn run(pool: PgPool,reporter: StatusReporter,Json(payload):Json<IndexRequest>, index: &str, req_url: &str)-> Result<Json<Value>, StatusCode>{
    //see type of request (default or target)and maybe get data or send it as is and also check for the api key if its not expired
    //identify type
    let mut user_id=None;
    let place: Value = if payload.req_type == "DEFAULT" {
        let api_key = &payload.api_key;
        match check_api(&pool, api_key).await {
            Ok(uid) => {
                user_id=Some(uid.clone());
                reporter.update("PROCESSING: Account verification", None,None,None,None).await;
                let result = sqlx::query("SELECT declared_geo_json FROM users WHERE user_id = $1")
                    .bind(&uid)
                    .fetch_one(&pool)
                    .await
                    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
                let geo: Value = result.try_get("declared_geo_json")
                    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
                geo
            }
            Err(_) => {
                reporter.update("FAILED: Authorization failure", None,None,None,None).await;
                return Err(StatusCode::UNAUTHORIZED)}
        }
    } else {
        Value::String(payload.city.clone())
    };
    //if type target then pass
    //if dafault check api and from the userid get the geojson
    //pass the type and the geojson accordingly
    reporter.update("PROCESSING: Running analyzation", None,None,None,None).await;
    //call python
    let to_send: serde_json::Value = serde_json::json!({
        "req_type": payload.req_type.clone(),
        "place": place.clone(),
        "index": index,
        "date1": payload.from.clone(),
        "date2": payload.till.clone()
    });
    let client = Client::new();
    let response = match client.post(req_url).json(&to_send).send().await {
        Ok(res) => {
            res
        },
        Err(e) => {
            reporter.update("FAILED: Request to python failed", None,None,None,None).await;
            eprintln!("Request failed: {e}");
            return Err(StatusCode::BAD_GATEWAY);
        }
    };
    let resp: Value = match response.json::<Value>().await {
        Ok(val) => {
            if payload.req_type == "DEFAULT" {
                reporter.update("DONE: Python analyzation successfull", Some(val.clone()), Some(payload), user_id.clone(), Some("INSERT INTO results (request_id, data) VALUES ($1, $2)".to_string())).await;
            } else {
                reporter.update("DONE: Python analyzation successfull", Some(val.clone()), Some(payload), Some(place.to_string()), Some("INSERT INTO results (request_id, data) VALUES ($1, $2)".to_string())).await;
            }
            val
        }
        Err(e) => {
            eprintln!("Failed to parse response JSON: {e}");
            reporter.update("FAILED", None,None,None,None).await;
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };
    Ok(Json(resp))
}

/* 
pub async fn get_geo_json(user_id: &str)-> Result<String, &'static str>{
    Ok("bruh".to_string())
}
*/