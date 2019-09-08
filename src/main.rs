use chrono::Utc;
use serde::Deserialize;

enum Date {
    Date(chrono::DateTime<Utc>),
    Range {
        start: chrono::DateTime<Utc>,
        end: chrono::DateTime<Utc>,
    },
}

#[derive(Debug, Deserialize)]
struct Theatre {
    name: String,
    url: String,
    root_url: String,
}

#[derive(Debug, Deserialize)]
struct Config {
    theatres: Vec<Theatre>,
}

fn main() {
    let fs = std::fs::File::open("config.json").unwrap();
    let config: Config = serde_json::from_reader(fs).unwrap();
    println!("{:?}", config);
}
