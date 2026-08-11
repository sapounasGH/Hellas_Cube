use sqlx::Pool;
use sqlx::Postgres;
//use axum::{http::StatusCode};
use sqlx::postgres::PgPoolOptions;//use sqlx::{PgPool, query};

pub async fn ping_database()-> Result<Pool<Postgres>, sqlx::Error>{

    //server and db connection starter
    //db credenstials for now is in a hidden file.
    dotenv::from_filename("/home/christossapounas/.hellascube/dbconfig.env").ok(); // TODO security problem here better usage is enviromental variable

    //getting the databae utl from the config file
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL not found in config");

    //making the connection and putting it inside a variable 
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;

    //returning the value
    Ok(pool)
}