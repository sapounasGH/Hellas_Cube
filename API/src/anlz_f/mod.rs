use axum::{Router, routing::get, routing::post, middleware::{self, Next}, http::Request, body::Body};
mod ndvi;
mod test;
mod ndti;
mod ndci;
mod ndwi;
mod ndmi;
mod ndbi;
mod ndsi;
mod wofs;
mod sdd;
mod user;

pub mod requests;

async fn log_request(req: Request<Body>, next: Next) -> impl axum::response::IntoResponse {
    let method = req.method().clone();
    let uri    = req.uri().clone();
    println!("➜ {} {}", method, uri);
    next.run(req).await
}

pub fn pathing()->Router{
    let app = Router::new()
        .route("/api", get(test::run))
        .route("/ndvi", post(ndvi::run))
        .route("/ndti",post(ndti::run))
        .route("/ndci",post(ndci::run))
        .route("/wofs",post(wofs::run))
        .route("/sdd", post(sdd::run))
        .route("/ndwi", post(ndwi::run))
        .route("/ndmi", post(ndmi::run))
        .route("/ndbi", post(ndbi::run))
        .route("/ndsi", post(ndsi::run))
        .route("/cacc", post(user::cacc))
        .layer(middleware::from_fn(log_request));
    app
}

pub async fn listening(app: Router){
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}