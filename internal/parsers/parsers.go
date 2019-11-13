package parsers

import (
	"log"

	"github.com/mindriot101/whatson/internal/config"
	"github.com/mindriot101/whatson/internal/fetchers"
)

type Parser struct{}

func NewParser(t *config.TheatreConfig, f fetchers.Fetcher) Parser {
	return Parser{}
}

func (p Parser) Ingest() {
	log.Println("Ingesting")
}
