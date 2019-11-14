package types

import "time"

type RawShow struct {
	Name      string    `json:"name"`
	Theatre   string    `json:"theatre"`
	ImageURL  string    `json:"image_url"`
	LinkURL   string    `json:"link_url"`
	StartDate time.Time `json:"start_date"`
	EndDate   time.Time `json:"end_date"`
}

func (s RawShow) ToShow() Show {
	return Show{
		Name:     s.Name,
		Theatre:  s.Theatre,
		ImageURL: s.ImageURL,
		LinkURL:  s.LinkURL,
		StartDate: Date{
			Day:   s.StartDate.Day(),
			Month: s.StartDate.Month(),
			Year:  s.StartDate.Year(),
		},
		EndDate: Date{
			Day:   s.EndDate.Day(),
			Month: s.EndDate.Month(),
			Year:  s.EndDate.Year(),
		},
	}
}

type Show struct {
	Name      string `json:"name"`
	Theatre   string `json:"theatre"`
	ImageURL  string `json:"image_url"`
	LinkURL   string `json:"link_url"`
	StartDate Date   `json:"start_date"`
	EndDate   Date   `json:"end_date"`
}

type Date struct {
	Day   int        `json:"day"`
	Month time.Month `json:"month"`
	Year  int        `json:"year"`
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
	Months []Month `json:"dates"`
}
