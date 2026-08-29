/*
DOCUMENDATION
*/

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
mod analysis_request;

use crate::analysis::requests::{IndexRequest, UserData, GeoJsonREQ, HistoryRequest};
use crate::analysis::requests::StatusReporter;

async fn log_request(State(pool): State<PgPool>,mut req: Request<Body>,next: Next) -> impl axum::response::IntoResponse {
    //Reporter logging status
    //getting a new reuqest
    let request_id = Uuid::new_v4().to_string();
    let method = req.method().clone();
    let uri    = req.uri().clone();
    println!("➜ {} {}", method, uri);

    //initializing the reporter waiter
    let (tx, mut rx) = mpsc::channel::<(String, Option<Value>, Option<IndexRequest>, Option<String>, Option<String>)>(10);
    req.extensions_mut().insert(StatusReporter { tx });

    //first status
    sqlx::query("INSERT INTO request_log_file (request_id, status) VALUES ($1::uuid, 'PENDING')")
        .bind(&request_id)
        .execute(&pool)
        .await
        .ok();

    //running the reporter
    let response = next.run(req).await;

    //waiting for response from the reporter to update request status
    while let Some((status, result, payload, shared_variable ,query)) = rx.recv().await {
        println!("► {} → {}", uri, status);
        if status.starts_with("DONE") {
            if let Some(result_data) = result {
                let result_id=Uuid::new_v4();
                let payload=payload.unwrap();
                let date_range = format!("[{},{})", &payload.from, &payload.till);
                match sqlx::query(&query.unwrap())
                    .bind(result_id)
                    .bind(payload.index)
                    .bind(shared_variable)
                    .bind(date_range)
                    .bind(result_data)
                    .bind(&request_id)
                    .execute(&pool)
                    .await{
                        Ok(_) => println!("Result saved"),
                        Err(e) => println!("Failed to save result, database error: {}", e),
                }
            }
        }
        sqlx::query("UPDATE request_log_file SET status = $1, status_timestamp = now() WHERE request_id = $2::uuid")
            .bind(&status)
            .bind(&request_id)
            .execute(&pool)
            .await
            .ok();
        if status.starts_with("DONE") || status.starts_with("FAILED") {
            println!("BREAKING");
            break;
        }
    }

    //responding the status
    response
}


//
pub fn pathing(pool: PgPool) -> Router {
    //ENDPOINTS

    Router::new()
        .route("/api", get(test::run))
        .route("/ndvi", post(|State(pool): State<PgPool>, 
            Extension(reporter): Extension<StatusReporter>, 
            body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndvi")
            }))
        .route("/ndti", post(|State(pool): State<PgPool>,
            Extension(reporter): Extension<StatusReporter>,
            body: Json<IndexRequest>| {
                analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndti")
            }))
        .route("/ndci", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndci")
        }))
        .route("/wofs", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/wofs")
        }))
        .route("/sdd", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/sdd")
        }))
        .route("/ndwi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndwi")
        }))
        .route("/ndmi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndmi")
        }))
        .route("/ndbi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndbi")
        }))
        .route("/ndsi", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<IndexRequest>| {
            analysis_request::run(pool, reporter, body, "http://localhost:8080/analyzation/ndsi")
        }))
        .route("/cacc", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<UserData>| user::cacc(pool, reporter,body)))
        .route("/login", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<UserData>| user::login(pool, reporter, body)))
        .route("/declare_geojson", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>,body: Json<GeoJsonREQ>| user::initialize_geo_json(pool, reporter,body)))
        .route("/history", post(|State(pool): State<PgPool>, Extension(reporter): Extension<StatusReporter>, body: Json<HistoryRequest>| user::history(pool, reporter, body)))
        .with_state(pool.clone())
        .layer(middleware::from_fn_with_state(pool.clone(), log_request))
}

//Starting the server
pub async fn listening(app: Router) {
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}