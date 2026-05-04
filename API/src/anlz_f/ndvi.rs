//use tokio::io::stdout;
//use std::process::Command;
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
        .post("http://localhost:8080/analyzation/ndvi")
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
    /*The old way nothing changed just saving maybe i need it in the future 
    let conda_python = "/home/christossapounas/.conda/envs/odc_env/bin/python3.10";
    let ct=payload.city.clone();
    let output = Command::new(conda_python)
        .arg("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/env_indexes.py")
        .arg(payload.city)
        .arg(payload.from)
        .arg(payload.till)
        .arg("NDVI")
        // Pass the conda env's bin to PATH so sub-imports work
        .env("PATH", "/home/christossapounas/.conda/envs/odc_env/bin:/home/christossapounas/miniforge3/condabin:/home/christossapounas/.cargo/bin:/home/christossapounas/.local/bin:/home/christossapounas/bin:/usr/local/bin:/usr/bin:/var/lib/snapd/snap/bin")
        .output()
        .expect("Failed to run Python script");
    let json_response = json!({
        "status": "OK",
        "analyzation": "NDVI",
        "Municipality":ct,
        "result": String::from_utf8_lossy(&output.stdout),
        "error": String::from_utf8_lossy(&output.stderr)
    });
    let resp=Json(json_response);
    return resp;
    */