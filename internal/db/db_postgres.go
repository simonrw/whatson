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

func (p PostgresDatabase) ShowsForMonth(q types.MonthQuery) ([]types.Show, error) {
	/*
		tx, err := p.db.Begin()
		if err != nil {
			return nil, err
		}
	*/

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

	return shows, nil
}

func (p PostgresDatabase) Close() {
	p.db.Close()
}
