/* 
File: main.rs
Author: Christos Sapounas
Latest Description Change: 22/07/2026 
Description: 
*/
mod analysis;
mod db;

//adding the tokio dependency
#[tokio::main]
async fn main() {  

    //log
    tracing_subscriber::fmt::init();

    //connecting to the database
    let pool=db::ping_database().await.expect("Failed connection to Database");

    //calling the listening function in analysis to start the API
    analysis::listening(analysis::pathing(pool)).await;
}