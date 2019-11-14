package scrapers

import (
	"log"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/mindriot101/whatson/internal/config"
	"github.com/mindriot101/whatson/internal/fetchers"
	"github.com/mindriot101/whatson/internal/types"
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

func (s Scraper) Ingest() ([]types.Show, error) {
	// Store the url so we can overwrite it if additional pages are needed.
	url := s.config.URL
	var shows []types.Show
	for {
		// Fetch the HTML using the fetcher
		html, err := s.fetcher.Fetch(url)
		if err != nil {
			log.Printf("error fetching html from %s\n", s.config.URL)
			return nil, err
		}
		log.Printf("fetched html from %s", url)

		// Parse the document
		doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
		if err != nil {
			log.Printf("error creaitng document from html\n")
			return nil, err
		}

		container := doc.Find(s.config.ContainerSelector)
		// childError := []string{}
		var show types.Show
		container.Children().Each(func(i int, l *goquery.Selection) {
			linkURL, exists := l.Find(s.config.LinkSelector).Attr("href")
			if !exists {
				// TODO: proper error handling
				// childError = append(childError, "cannot find link url")
				return
			}

			if s.config.LinkRelative {
				linkURL = s.config.RootURL + linkURL
			}

			imageURL, exists := l.Find(s.config.ImageSelector).Attr("src")
			if !exists {
				// TODO: proper error handling
				// childError = append(childError, fmt.Sprintf("cannot find image url %d", i))
				return
			}

			if s.config.LinkRelative {
				imageURL = s.config.RootURL + imageURL
			}

			shows = append(shows, show)

		})

		// TODO: proper error handling
		/*
			if len(childError) > 0 {
				for _, e := range childError {
					log.Printf("parsing error: %s\n", e)
				}
				return nil, fmt.Errorf("error parsing html")
			}
		*/

		if s.config.NextSelector == "" {
			// We do not have a next page defined, so all of the theatres must
			// have been on the first page returned by the fetcher.
			break
		}
	}

	return shows, nil
}
