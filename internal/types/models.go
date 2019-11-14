package types

import "time"

type Show struct {
	Name      string
	Theatre   string
	ImageURL  string
	LinkURL   string
	StartDate time.Time
	EndDate   time.Time
}

// Api type
type Shows struct {
	Shows []Show `json:"shows"`
}

type Month struct {
	Month int64 `json:"month"`
	Year  int64 `json:"year"`
}

type Months struct {
	Months []Month `json:"months"`
}
