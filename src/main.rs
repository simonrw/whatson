use select::document::Document;
use select::predicate::{Attr, Class, Name, Predicate, Text};
use serde::Deserialize;
use std::error::Error;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

fn month_str_to_int(s: &str) -> Result<i8> {
    match s {
        "January" => Ok(0),
        "February" => Ok(1),
        "March" => Ok(2),
        "April" => Ok(3),
        "May" => Ok(4),
        "June" => Ok(5),
        "July" => Ok(6),
        "August" => Ok(7),
        "September" => Ok(8),
        "October" => Ok(9),
        "November" => Ok(10),
        "December" => Ok(11),
        _ => Err(format!("{} is not a month", s).into()),
    }
}

fn date_from_text(s: &str, year: u32) -> Result<Date> {
    if s.contains("-") {
        let mut parts = s.split("-").map(|s| s.trim());
        let start = match date_from_text(parts.next().unwrap(), year) {
            Ok(Date::Date(r)) => r,
            Ok(_) => return Err(format!("invalid date format").into()),
            Err(e) => return Err(e),
        };
        let end = match date_from_text(parts.next().unwrap(), year) {
            Ok(Date::Date(r)) => r,
            Ok(_) => return Err(format!("invalid date format").into()),
            Err(e) => return Err(e),
        };

        Ok(Date::Range { start, end })
    } else {
        let mut chars = s.chars();
        let day_chars: String = chars.clone().take_while(|c| c.is_digit(10)).collect();
        let month_chars: String = chars.skip_while(|c| *c != ' ').skip(1).collect();

        let day: i32 = day_chars.parse().unwrap();
        let month = month_str_to_int(&month_chars)?;
        Ok(Date::Date(RawDate { day, month, year }))
    }
}

#[derive(Debug)]
struct RawDate {
    day: i32,
    month: i8,
    year: u32,
}

#[derive(Debug)]
enum Date {
    Date(RawDate),
    Range { start: RawDate, end: RawDate },
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

#[derive(Debug)]
struct Show {
    name: String,
    date: Date,
}

fn extract_theatre(t: &Theatre) -> Result<Vec<Show>> {
    let body = reqwest::get(&t.url)?.text()?;

    let document = Document::from(body.as_str());
    let container = document
        .find(Name("div").and(Class("list-productions")))
        .into_selection();

    let mut year: Option<u32> = None;

    let mut shows = Vec::new();
    for child in container.children().iter() {
        if child.is(Name("div")) {
            if child.is(Class("production-list-item")) {
                assert!(year.is_some());
                let details = child
                    .find(Name("div").and(Class("production-details")))
                    .into_selection();
                let title = details.find(Name("h3")).first().unwrap().text();

                let date_text = details
                    .find(Name("p").and(Class("date")))
                    .first()
                    .unwrap()
                    .text();

                // Handle the date text: if it is a single date, then construct that, otherwise
                // construct a date range
                let date = date_from_text(&date_text, year.clone().unwrap())?;

                shows.push(Show { name: title, date });
            }
        } else if child.is(Name("h2")) {
            let date_text = child.text();
            let mut parts = date_text.split_whitespace();
            let _ = parts.next().unwrap();
            year = Some(parts.next().unwrap().parse().unwrap());
        } else {
            continue;
        }
    }

    Ok(shows)
}

fn main() {
    let fs = std::fs::File::open("config.json").unwrap();
    let config: Config = serde_json::from_reader(fs).unwrap();

    let results: Vec<_> = config.theatres.iter().map(extract_theatre).collect();
    println!("{:?}", results);
}
