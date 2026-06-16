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

pub async fn run(pool: PgPool,reporter: StatusReporter,Json(payload):Json<IndexRequest>, req_url: &str)-> Result<Json<Value>, StatusCode>{
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
        }else if payload.req_type == "TARGET"{
            let city = payload.city.clone();
            Value::String(city)
        }else{
            Value::Null
        };
    //if type target then pass
    //if dafault check api and from the userid get the geojson
    //pass the type and the geojson accordingly
    let place_value = if payload.req_type == "DEFAULT" {
        serde_json::json!(place.to_string())  // serialize GeoJSON object → JSON string
    } else {
        serde_json::json!(place.as_str().unwrap_or(""))
    };
    reporter.update("PROCESSING: Running analyzation", None,None,None,None).await;
    //call python for analyzation (basically we are calling the Internal Python API)
    let to_send: serde_json::Value = serde_json::json!({
        "req_type": payload.req_type.clone(),
        "place": place_value,
        "index": payload.index.clone(),
        "date1": payload.from.clone(),
        "date2": payload.till.clone()
    });
    //println!("{:#}", to_send); 
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
                reporter.update("DONE: Python analyzation successfull", Some(val.clone()), Some(payload), user_id.clone(), Some("INSERT INTO user_results (res_id, analysis, user_id, date_range, res_json, request_id) VALUES ($1, $2, $3, $4::daterange, $5, $6)".to_string())).await;
            } else {
                reporter.update("DONE: Python analyzation successfull", Some(val.clone()), Some(payload), place.as_str().map(|s| s.to_string()), Some("INSERT INTO general_results (res_id, analysis, area_name, date_range, res_json, request_id) VALUES ($1, $2, $3, $4::daterange, $5, $6)".to_string())).await;
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