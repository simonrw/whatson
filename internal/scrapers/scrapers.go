package scrapers

import (
	"log"

	"github.com/mindriot101/whatson/internal/config"
	"github.com/mindriot101/whatson/internal/db"
	"github.com/mindriot101/whatson/internal/fetchers"
)

type Scraper struct {
	config  *config.TheatreConfig
	fetcher fetchers.Fetcher
}

func NewScraper(t *config.TheatreConfig, f fetchers.Fetcher) Scraper {
	return Scraper{
		config:  t,
		fetcher: f,
	}
}

func (s Scraper) Ingest(db db.Database) error {
	// Store the url so we can overwrite it if additional pages are needed.
	url := s.config.URL
	for {
		// Fetch the HTML using the fetcher
		html, err := s.fetcher.Fetch(url)
		if err != nil {
			log.Printf("error fetching html from %s\n", s.config.URL)
			return err
		}
		_ = html
	}
}
