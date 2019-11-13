package fetchers

import "fmt"

type Fetcher interface {
	Fetch(url string) (string, error)
}

var fetchers = map[string]Fetcher{
	"stdlib": StdlibFetcher{},
}

func GetFetcher(name string) (*Fetcher, error) {
	fetcher, ok := fetchers[name]
	if !ok {
		return nil, fmt.Errorf("no fetcher named %s available", name)
	}
	return &fetcher, nil
}
