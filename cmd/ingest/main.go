package main

import (
	"io/ioutil"
	"log"

	"github.com/BurntSushi/toml"
	"github.com/joho/godotenv"
	"github.com/mindriot101/whatson/internal/config"
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

	for _, theatre := range currentConfig.Theatres {
		fetcher, err := fetchers.GetFetcher(theatre.Fetcher)
		if err != nil {
			log.Fatal(err)
		}

		s := scrapers.NewScraper(theatre, *fetcher)
		// TODO: include the database in this
		// TODO: parallelise
		// s.Ingest()
		_ = s
	}
}
