use axum::{Router,routing::get, routing::post};

mod ndvi;
mod test;
mod ndti;
mod ndci;
mod wofs;
pub mod requests;


pub fn pathing()->Router{
    println!("Called API!");
    let app = Router::new()
        .route("/api", get(test::run))
        .route("/ndvi", post(ndvi::run))
        .route("/ndti",post(ndti::run))
        .route("/ndci",post(ndci::run))
        .route("/wofs",post(wofs::run));
    app
}

pub async fn listening(app: Router){
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server started successfully at 0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}