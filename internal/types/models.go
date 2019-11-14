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
