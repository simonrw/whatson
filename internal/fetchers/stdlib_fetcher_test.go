package fetchers

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
)

type handler struct{}

func (handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "ok")
}

func TestFetcher(t *testing.T) {
	var h handler
	server := httptest.NewServer(h)

	response, err := NewStdlibFetcher().Fetch(server.URL)
	if err != nil {
		t.Errorf("got non-nil response from fetcher: %v\n", err)
	}

	if response != "ok" {
		t.Errorf("incorrect response, expected `ok`, got `%s`", response)
	}
}
