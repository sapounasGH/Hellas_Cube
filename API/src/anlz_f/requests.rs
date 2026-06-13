use serde::Deserialize;
use tokio::sync::mpsc;
use serde_json::Value;

#[derive(Deserialize)]
pub struct IndexRequest {
    pub req_type: String,
    pub api_key: String,
    pub city: String,
    pub from: String,
    pub till: String
}

#[derive(Deserialize)]
pub struct UserData{
    pub email: String,
    pub password: String
}

#[derive(Deserialize)]
pub struct GeoJsonREQ{
    pub api_key: String,
    pub geo_json: String
}


#[derive(Clone)]
pub struct StatusReporter {
    pub tx: mpsc::Sender<(String, Option<Value>,Option<IndexRequest>, Option<String>, Option<String>)>,
}

impl StatusReporter {
    pub async fn update(&self, status: &str, result: Option<Value>, payload: Option<IndexRequest>, place_or_userid: Option<String>, querry: Option<String>) {
        self.tx.send((status.to_string(), result,payload,place_or_userid, querry)).await.ok();
    }
}