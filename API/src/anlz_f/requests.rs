use serde::Deserialize;

#[derive(Deserialize)]
pub struct IndexRequest {
    pub city: String,
    pub from: String,
    pub till: String
}

#[derive(Deserialize)]
pub struct UserData{
    pub email: String,
    pub password: String
}