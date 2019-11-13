package main

import (
	"io/ioutil"
	"log"

	"github.com/BurntSushi/toml"
)

type theatreConfig struct {
	name string
}

type whatsonConfig struct {
	theatres []*theatreConfig `toml:"theatre"`
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
}
