package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/BurntSushi/toml"
)

type theatreConfig struct {
	Name    string `toml:"name"`
	Active  bool   `toml:"active"`
	RootURL string `toml:"root-url"`
	URL     string `toml:"url"`
}

type whatsonConfig struct {
	Theatres []*theatreConfig `toml:"theatre"`
}

func (w whatsonConfig) String() string {
	b, err := json.Marshal(w)
	if err != nil {
		return fmt.Sprintf("error")
	}
	return string(b)
}

func main() {
	// TODO: put this in command line options
	configFilename := "config.toml"
	dat, err := ioutil.ReadFile(configFilename)
	if err != nil {
		log.Fatal(err)
	}

	var currentConfig whatsonConfig
	if _, err = toml.Decode(string(dat), &currentConfig); err != nil {
		log.Fatal(err)
	}

	fmt.Println(currentConfig)
}
