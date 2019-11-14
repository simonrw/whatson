package scrapers

import (
	"io/ioutil"
	"log"
	"path"
	"runtime"
	"testing"

	"github.com/BurntSushi/toml"
	"github.com/mindriot101/whatson/internal/config"
)

// Mock fetcher implementation that returns known HTML content
type AlbanyFetcher struct {
	FetchCalls int
}

func (a *AlbanyFetcher) Fetch(url string) (string, error) {
	a.FetchCalls++
	log.Printf("mock fetcher querying %s\n", url)

	// Have to monkey about with the path to get the actual path as go changes
	// working directory to the module directory before executing tests. This
	// is definitely not expected behaviour, but nevermind.
	_, filename, _, _ := runtime.Caller(0)
	rootDir := path.Join(path.Dir(filename), "..", "..")

	// read the test fixture data
	b, err := ioutil.ReadFile(path.Join(rootDir, "fixtures/test_parse_albany.html"))
	if err != nil {
		return "", err
	}

	return string(b), nil
}

func TestAlbany(t *testing.T) {

	// Have to monkey about with the path to get the actual path as go changes
	// working directory to the module directory before executing tests. This
	// is definitely not expected behaviour, but nevermind.
	_, filename, _, _ := runtime.Caller(0)
	rootDir := path.Join(path.Dir(filename), "..", "..")
	configFilename := path.Join(rootDir, "config.toml")
	text, err := ioutil.ReadFile(configFilename)

	var currentConfig config.WhatsonConfig
	if _, err = toml.Decode(string(text), &currentConfig); err != nil {
		log.Fatal(err)
	}

	// Get the theatre config for the Albany theatre
	var theatreConfig config.TheatreConfig
	found := false

	for _, theatre := range currentConfig.Theatres {
		if theatre.Name == "albany" {
			theatreConfig = *theatre
			found = true
			break
		}
	}
	if !found {
		t.Errorf("cannot find albany config in current config file")
	}

	f := &AlbanyFetcher{
		FetchCalls: 0,
	}

	scraper := NewScraper(&theatreConfig, f)
	shows, err := scraper.Ingest()
	if err != nil {
		t.Errorf("error with ingestion: %+v\n", err)
	}

	if f.FetchCalls != 1 {
		t.Errorf("Fetcher.Fetch not called the correct number of times (once), called %d times", f.FetchCalls)
	}

	if len(shows) != 49 {
		t.Errorf("incorrect number of shows, found %d, expected 49", len(shows))
	}
}
