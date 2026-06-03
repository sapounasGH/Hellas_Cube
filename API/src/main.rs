mod anlz_f;
mod db_conn;

#[tokio::main]
async fn main() {  
    tracing_subscriber::fmt::init();  
    let pool=db_conn::ping_database().await.expect("Failed connection to Database");
    anlz_f::listening(anlz_f::pathing(pool)).await;
}