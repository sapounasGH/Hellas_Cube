use axum::{Json, response::IntoResponse};
use serde_json::json;
//use tokio::io::stdout;
use std::process::Command;
use crate::anlz_f::requests::{IndexRequest};

pub async fn run(Json(payload):Json<IndexRequest>)-> impl IntoResponse{
    //calling python
    let conda_python = "/home/christossapounas/.conda/envs/odc_env/bin/python3.10";
    let ct=payload.city.clone();
    let output = Command::new(conda_python)
        .arg("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/env_indexes.py")
        .env("AWS_ACCESS_KEY_ID", "")
        .env("AWS_SECRET_ACCESS_KEY", "")
        .env("AWS_DEFAULT_REGION", "us-west-2")
        .env("AWS_REQUEST_PAYER", "requester")
        .arg(payload.city)
        .arg(payload.from)
        .arg(payload.till)
        .arg("FLOOD_WOFS")
        // Pass the conda env's bin to PATH so sub-imports work
        .env("PATH", "/home/christossapounas/.conda/envs/odc_env/bin:/home/christossapounas/miniforge3/condabin:/home/christossapounas/.cargo/bin:/home/christossapounas/.local/bin:/home/christossapounas/bin:/usr/local/bin:/usr/bin:/var/lib/snapd/snap/bin")
        .output()
        .expect("Failed to run Python script");
    let json_response = json!({
        "status": "OK",
        "analyzation": "FLOOD_WOFS",
        "Municipality":ct,
        "result": String::from_utf8_lossy(&output.stdout),
        "error": String::from_utf8_lossy(&output.stderr)
    });
    let resp=Json(json_response);
    return resp;
}