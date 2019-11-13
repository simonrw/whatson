package fetchers

import (
	"io/ioutil"
	"log"
	"net/http"
)

type StdlibFetcher struct {
}

func NewStdlibFetcher() StdlibFetcher {
	return StdlibFetcher{}
}

func (f StdlibFetcher) Fetch(url string) (string, error) {
	// TODO: use request with context
	r, err := http.Get(url)
	if err != nil {
		log.Printf("error fetching http response from %s\n", url)
		return "", err
	}
	defer r.Body.Close()

	b, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Println("error reading response body")
		return "", nil
	}

	return string(b), nil
}
