use serde::Deserialize;

#[derive(Deserialize)]
pub struct NDVIRequest {  // match whatever you use in the handler
    pub city: String,
    pub from: String,
    pub till: String
}