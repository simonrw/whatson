package main

import (
	"fmt"
	"io/ioutil"
	"log"

	"github.com/BurntSushi/toml"
	"github.com/mindriot101/whatson/internal/config"
)

func main() {
	// TODO: put this in command line options
	configFilename := "config.toml"
	dat, err := ioutil.ReadFile(configFilename)
	if err != nil {
		log.Fatal(err)
	}

	var currentConfig config.WhatsonConfig
	if _, err = toml.Decode(string(dat), &currentConfig); err != nil {
		log.Fatal(err)
	}

	fmt.Println(currentConfig)
}
