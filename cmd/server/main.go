package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"text/template"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/mindriot101/whatson/internal/db"
	"github.com/mindriot101/whatson/internal/types"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal(err)
	}

	// Set up the database
	db, err := db.Connect("postgres", os.Getenv("DATABASE_CONN"))
	if err != nil {
		log.Fatal(err)
	}

	// Load the template from disk
	templateFilename := "whatson/templates/index.html"
	s, err := ioutil.ReadFile(templateFilename)
	if err != nil {
		log.Fatalf("error loading template from %s\n", templateFilename)
	}

	t, err := template.New("index").Parse(string(s))
	if err != nil {
		log.Fatalf("error parsing template %s\n", templateFilename)
	}

	// Set up the HTTP server
	r := mux.NewRouter()
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Println("got request")
		t.Execute(w, nil)
	})

	// Set up static file handling
	fs := http.FileServer(http.Dir("whatson/static"))
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", fs))

	// TODO: Set up API endpoints
	r.HandleFunc("/api/shows", func(w http.ResponseWriter, r *http.Request) {
		log.Println("got request")

		var q types.MonthQuery
		err := json.NewDecoder(r.Body).Decode(&q)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		shows, err := db.ShowsForMonth(q)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		if err = json.NewEncoder(w).Encode(shows); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

	}).Methods("POST")

	r.HandleFunc("/api/months", func(w http.ResponseWriter, r *http.Request) {
		log.Println("got request for months")

		months, err := db.Months()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		if err = json.NewEncoder(w).Encode(months); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	})

	// Run the server
	srv := &http.Server{
		Handler:      r,
		Addr:         "127.0.0.1:8080",
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Println("listening on :8080")
	err = srv.ListenAndServe()
	if err != nil {
		log.Fatalf("server failed: %v\n", err)
	}
}
