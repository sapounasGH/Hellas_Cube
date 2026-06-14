use std::result;

use axum::{
    Router,
    routing::{get, post},
    middleware::{self, Next},
    http::Request,
    body::Body,
    extract::{Json, State, Extension},
};
use sqlx::PgPool;
use uuid::Uuid;
use serde_json::Value;
use tokio::sync::mpsc;

mod test;
mod user;
pub mod requests;
mod analyzation_request;

use crate::anlz_f::requests::{IndexRequest, UserData, GeoJsonREQ};
use crate::anlz_f::requests::StatusReporter;

//PUT SOME OOP IN THE WHOLE OF THE API

async fn log_request(State(pool): State<PgPool>,mut req: Request<Body>,next: Next) -> impl axum::response::IntoResponse {
    //EXPLAIN THE LOGIC
    let request_id = Uuid::new_v4().to_string();
    let method = req.method().clone();
    let uri    = req.uri().clone();
    println!("➜ {} {}", method, uri);
    let (tx, mut rx) = mpsc::channel::<(String, Option<Value>, Option<IndexRequest>, Option<String>, Option<&str>)>(10);
    req.extensions_mut().insert(StatusReporter { tx });
    sqlx::query("INSERT INTO request_log_file (request_id, status) VALUES ($1, 'PENDING')")
        .bind(&request_id)
        .execute(&pool)
        .await
        .ok();
    let response = next.run(req).await;
    while let Some((status, result, payload, shared_variable ,querry)) = rx.recv().await {
        println!("► {} → {}", uri, status);
        if status == "DONE: Python analyzation successfull" {
            if let Some(data) = result {
                let result_id=Uuid::new_v4();
                let payload=payload.unwrap();
                let result=result.unwrap();
                let date_range = format!("[{},{}]", &payload.date_from, &payload.date_till);
                sqlx::query(querry.unwrap())
                    .bind(result_id)
                    .bind(payload.index)
                    .bind(shared_variable)
                    .bind(date_range)
                    .bind(result)
                    .bind(&request_id)
                    .execute(&pool)
                    .await
                    .ok();
            }
        }
        sqlx::query("UPDATE request_log_file SET status = $1, status_timestamp = now() WHERE request_id = $2")
            .bind(&status)
            .bind(&request_id)
            .execute(&pool)
            .await
            .ok();
        if status.starts_with("DONE") || status.starts_with("FAILED") {
            break;
        }
    }
    response
}

pub fn pathing(pool: PgPool) -> Router {
    Router::new()
        .route("/api", get(test::run))
        .route("/ndvi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndvi")
        }))
        .route("/ndti", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndti")
        }))
        .route("/ndci", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndci")
        }))
        .route("/wofs", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/wofs")
        }))
        .route("/sdd", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/sdd")
        }))
        .route("/ndwi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndwi")
        }))
        .route("/ndmi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndmi")
        }))
        .route("/ndbi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndbi")
        }))
        .route("/ndsi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analyzation_request::run(pool, reporter, body,  "http://localhost:8080/analyzation/ndsi")
        }))
        .route("/cacc", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<UserData>| user::cacc(pool, reporter,body)))
        .route("/login", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<UserData>| user::login(pool, reporter, body)))
        .route("/declare_geojson", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<GeoJsonREQ>| user::initialize_geo_json(pool, reporter,body)))
        .with_state(pool.clone())
        .layer(middleware::from_fn_with_state(pool.clone(), log_request))
}

pub async fn listening(app: Router) {
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}