package scrapers

import (
	"log"

	"github.com/mindriot101/whatson/internal/config"
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

func (s Scraper) Ingest() {
	log.Println("Ingesting")
}
