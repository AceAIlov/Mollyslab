use std::env;
use reqwest::blocking::Client;
use serde::Deserialize;

#[derive(Deserialize)]
struct EmotionResponse {
    feeling: String,
    temperature: f32,
    text: String,
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 || args[1] != "run" {
        eprintln!("Usage: azumi run <message>");
        return;
    }
    let message = &args[2..].join(" ");
    let client = Client::new();
    let url = "http://localhost:8000/emotion";
    let payload = serde_json::json!({ "text": message });
    let res = client.post(url)
        .json(&payload)
        .send()
        .expect("Failed to contact API");

    if let Ok(parsed) = res.json::<EmotionResponse>() {
        println!("感情: {}  温度: {:.2}\n応答: {}", parsed.feeling, parsed.temperature, parsed.text);
    } else {
        println!("Error: could not parse response");
    }
}

