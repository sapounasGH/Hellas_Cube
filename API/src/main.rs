use axum::{Json, Router, response::IntoResponse, routing::get};
use serde_json::json;

#[tokio::main]
async fn main() {
    let app = Router::new().route("/api", get(hello_world));

    // listen globally on port 3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}

async fn hello_world() -> impl IntoResponse {
    let json_response = json!({
        "status": "ok",
        "message": "Hello, World!"
    });
    Json(json_response)
}