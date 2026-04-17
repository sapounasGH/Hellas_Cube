use std::process::Command;
use axum::{response::IntoResponse};
use axum::{Json};
use serde_json::json;

pub async fn run() -> impl IntoResponse {
    //calling python
    let conda_python = "/home/christossapounas/.conda/envs/odc_env/bin/python3.10";
    let output = Command::new(conda_python)
        .arg("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/test_script.py")
        // Pass the conda env's bin to PATH so sub-imports work
        .env("PATH", "/home/christossapounas/miniforge3/bin:/usr/bin:/bin")
        .env("CONDA_PREFIX", "/home/christossapounas/.conda/envs/odc_env/bin:/home/christossapounas/miniforge3/condabin:/home/christossapounas/.cargo/bin:/home/christossapounas/.local/bin:/home/christossapounas/bin:/usr/local/bin:/usr/bin:/var/lib/snapd/snap/bin")
        .env("PROJ_DATA", "/home/christossapounas/.conda/envs/odc_env/share/proj")
        .output()
        .expect("Failed to run Python script");
    let json_response = json!({
        "status": "OK",
        "analyzation": "NDVI",
        "result": String::from_utf8_lossy(&output.stdout)
    });
    let resp=Json(json_response);
    return resp;
}