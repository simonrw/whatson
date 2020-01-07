# Whatson

What is on at local theatres?  A web app to collect the event listings of local
theatres by web scraping.

## Implementation

The server is a simple Flask app, connected to a Postgresql database. The
frontend is written in Elm.

A separate script (`whatson-ingest`) performs the actual scraping. Theatres are
configured in `config.ini`. This scrapes the theatre websites and places the
entries in the database for presenting via the Flask app.

## Installation

For both the frontend and backend, the database connection is supplied via
environment variables. The postgres connection url is supplied with the
`$DATABASE_URL` variable.

### Backend

`poetry install`

### Frontend

`npm run prod`
