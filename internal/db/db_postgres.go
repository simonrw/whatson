package db

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
	"github.com/mindriot101/whatson/internal/types"
)

type PostgresDatabase struct {
	db *sql.DB
}

func (p PostgresDatabase) ShowsForMonth(q types.MonthQuery) (*types.Shows, error) {
	rows, err := p.db.Query(`
		select name, theatre, image_url, link_url, start_date, end_date
		from shows
		where extract(month from start_date) >= $1
		and extract(year from start_date) >= $2
		and extract(month from end_date) <= $1
		and extract(year from end_date) <= $2
	`, q.Month, q.Year)
	if err != nil {
		log.Printf("sql error: %+v\n", err)
		return nil, err
	}
	defer rows.Close()

	shows := []types.Show{}
	var show types.Show
	for rows.Next() {
		err := rows.Scan(&show.Name, &show.Theatre, &show.ImageURL, &show.LinkURL, &show.StartDate, &show.EndDate)
		if err != nil {
			return nil, err
		}

		shows = append(shows, show)
	}

	return &types.Shows{Shows: shows}, nil
}

func (p PostgresDatabase) Months() (*types.Months, error) {
	rows, err := p.db.Query(`
		select
		extract(month from start_date) as start_month,
		extract(year from start_date) as start_year,
		extract(month from end_date) as end_month,
		extract(year from end_date) as end_year
		from shows
	`)
	if err != nil {
		log.Printf("sql error: %+v\n", err)
		return nil, err
	}
	defer rows.Close()

	// Go does not have a set type, so we must use the keys of a map to get uniqueness.
	uniqueMonthYears := make(map[types.Month]bool)
	var sm, sy, em, ey int64
	for rows.Next() {
		err := rows.Scan(&sm, &sy, &em, &ey)
		if err != nil {
			return nil, err
		}

		// Start date
		m := types.Month{
			Month: sm,
			Year:  sy,
		}
		uniqueMonthYears[m] = true

		// End date
		m = types.Month{
			Month: em,
			Year:  ey,
		}
		uniqueMonthYears[m] = true
	}

	months := []types.Month{}
	for k := range uniqueMonthYears {
		months = append(months, k)
	}

	return &types.Months{Months: months}, nil
}

func (p PostgresDatabase) Close() {
	p.db.Close()
}
