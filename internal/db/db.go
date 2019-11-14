package db

import (
	"database/sql"
	"fmt"

	"github.com/mindriot101/whatson/internal/types"
)

type Database interface {
	ShowsForMonth(types.MonthQuery) (*types.Shows, error)
	Months() (*types.Months, error)
	Close()
}

func Connect(t string, c string) (Database, error) {
	switch t {
	case "postgres":
		db, err := sql.Open("postgres", c)
		if err != nil {
			return nil, err
		}
		return PostgresDatabase{db: db}, nil
	default:
		return nil, fmt.Errorf("invalid database type: %s\n", t)
	}
}
