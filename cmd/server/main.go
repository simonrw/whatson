package main

import (
	"io/ioutil"
	"log"
	"net/http"
	"text/template"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
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
