package db

type Database interface {
	Connect() (*Database, error)
}
