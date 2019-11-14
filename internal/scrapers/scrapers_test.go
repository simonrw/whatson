package scrapers

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/mindriot101/whatson/internal/config"
	"github.com/mindriot101/whatson/internal/fetchers"
)

type handler struct{}

func (handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "ok")
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

	f := fetchers.NewStdlibFetcher()

	scraper := NewScraper(&theatreConfig, f)
	_ = scraper
}
