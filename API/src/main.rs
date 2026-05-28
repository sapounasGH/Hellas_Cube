mod anlz_f;
use sqlx::postgres::PgPoolOptions;

#[tokio::main]
async fn main() {  
    //server and db connection starter
    //db url for now is in a hidden file.
    tracing_subscriber::fmt::init();  
    anlz_f::listening(anlz_f::pathing()).await;
    dotenv::from_filename("/home/youruser/.hellascube/config.env").ok();
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL not found in config");
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("Failed to connect to DB");
}