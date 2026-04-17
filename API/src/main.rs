mod anlz_f;
//HTTP
#[tokio::main]
async fn main() {    
    anlz_f::listening(anlz_f::pathing()).await;
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