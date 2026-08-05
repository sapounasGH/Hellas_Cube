mod analysis;
mod db;

#[tokio::main]
async fn main() {  
    tracing_subscriber::fmt::init();  
    let pool=db::ping_database().await.expect("Failed connection to Database");
    analysis::listening(analysis::pathing(pool)).await;
}