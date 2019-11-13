package fetcher

type Fetcher interface {
	Fetch(url string) (string, error)
}
