package config

import (
	"encoding/json"
	"fmt"
)

type TheatreConfig struct {
	Name              string `toml:"name"`
	Active            bool   `toml:"active"`
	RootURL           string `toml:"root-url"`
	URL               string `toml:"url"`
	Fetcher           string `toml:"fetcher"`
	ContainerSelector string `toml:"container-selector"`
	LinkSelector      string `toml:"link-selector"`
	ImageSelector     string `toml:"image-selector"`
	TitleSelector     string `toml:"title-selector"`
	DateSelector      string `toml:"date-selector"`
	LinkRelative      bool   `toml:"link-relative"`
	NextSelector      string `toml:"next-selector"`
}

type WhatsonConfig struct {
	Theatres []*TheatreConfig `toml:"theatre"`
}

func (w WhatsonConfig) String() string {
	b, err := json.Marshal(w)
	if err != nil {
		return fmt.Sprintf("error")
	}
	return string(b)
}
