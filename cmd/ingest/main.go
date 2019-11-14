package main

import (
	"io/ioutil"
	"log"
	"os"

	"github.com/BurntSushi/toml"
	"github.com/joho/godotenv"
	"github.com/mindriot101/whatson/internal/config"
	"github.com/mindriot101/whatson/internal/db"
	"github.com/mindriot101/whatson/internal/fetchers"
	"github.com/mindriot101/whatson/internal/scrapers"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal(err)
	}

	// TODO: put this in command line options
	configFilename := "config.toml"
	dat, err := ioutil.ReadFile(configFilename)
	if err != nil {
		log.Fatal(err)
	}

	var currentConfig config.WhatsonConfig
	if _, err = toml.Decode(string(dat), &currentConfig); err != nil {
		log.Fatal(err)
	}

	// Set up the database
	db, err := db.Connect("postgres", os.Getenv("DATABASE_CONN"))
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	log.Println("connected to the database")

	for _, theatre := range currentConfig.Theatres {
		log.Printf("ingesting theatre %+v\n", theatre)
		fetcher, err := fetchers.GetFetcher(theatre.Fetcher)
		if err != nil {
			log.Fatal(err)
		}

		s := scrapers.NewScraper(theatre, *fetcher)
		// TODO: parallelise
		shows, err := s.Ingest()
		if err != nil {
			log.Fatal(err)
		}

		// Upload the shows to the database
		for _, show := range shows {
			if err = db.Upload(show); err != nil {
				// TODO: make sure to not fail on integrity errors
				log.Fatal(err)
			}
		}
	}
}
