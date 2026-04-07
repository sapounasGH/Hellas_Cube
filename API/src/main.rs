use axum::{Json, Router, response::IntoResponse, routing::get, routing::post};
use serde_json::json;
use std::process::Command;
use serde::Deserialize;

//HTTP
#[tokio::main]
async fn main() {    
    listening(pathing()).await;
}

fn pathing()->Router{
    let app = Router::new()
        .route("/api", get(test))
        .route("/ndvi", post(ndvi_anal));
    app
}

async fn listening(app: Router){
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}


async fn ndvi_anal(Json(payload):Json<NDVIRequest>)-> impl IntoResponse{
    //calling python
    let conda_python = "/home/christossapounas/.conda/envs/odc_env/bin/python3.10";
    let output = Command::new(conda_python)
        .arg("/run/media/christossapounas/AEGON/Thesis_Hellas_Cube/Hellas_Cube/P_analyzations_HC/ndvi.py")
        .arg(payload.city)
        // Pass the conda env's bin to PATH so sub-imports work
        .env("PATH", "/home/christossapounas/miniforge3/bin:/usr/bin:/bin")
        .env("CONDA_PREFIX", "/home/christossapounas/.conda/envs/odc_env/bin:/home/christossapounas/miniforge3/condabin:/home/christossapounas/.cargo/bin:/home/christossapounas/.local/bin:/home/christossapounas/bin:/usr/local/bin:/usr/bin:/var/lib/snapd/snap/bin")
        .output()
        .expect("Failed to run Python script");
    let json_response = json!({
        "status": "OK",
        "analyzation": "NDVI",
        "Municipality":payload.city,
        "stdout": String::from_utf8_lossy(&output.stdout),
        "stderr": String::from_utf8_lossy(&output.stderr)
    });
    let resp=Json(json_response);
    return resp;
}

//continue testing to call a python file from rust
async fn test() -> impl IntoResponse {
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
        "stdout": String::from_utf8_lossy(&output.stdout)
    });
    let resp=Json(json_response);
    return resp;
}

#[derive(Deserialize)]
struct NDVIRequest {  // match whatever you use in the handler
    city: String,
}
/*
HTTPS

use axum::{Json, Router, response::IntoResponse, routing::get};
use axum_server::tls_rustls::RustlsConfig;
use serde_json::json;
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    let config = RustlsConfig::from_pem_file(
        "cert.pem",  // your certificate
        "key.pem",   // your private key
    )
    .await
    .unwrap();

    let app = Router::new().route("/api", get(hello_world));

    let addr = SocketAddr::from(([0, 0, 0, 0], 443));
    println!("Server started at https://0.0.0.0:443");
    axum_server::bind_rustls(addr, config)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
*/