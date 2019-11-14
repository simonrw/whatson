package scrapers

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/mindriot101/whatson/internal/config"
)

type handler struct{}

func (handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "ok")
}

// Mock fetcher implementation that returns known HTML content
type AlbanyFetcher struct{}

func (AlbanyFetcher) Fetch(url string) (string, error) {
	return "", nil
}

func TestAlbany(t *testing.T) {

	h := handler{}
	server := httptest.NewServer(h)

	theatreConfig := config.TheatreConfig{
		Name:    "albany",
		Active:  true,
		RootURL: "",
		URL:     server.URL,
	}

	f := AlbanyFetcher{}

	scraper := NewScraper(&theatreConfig, f)
	_ = scraper
}
