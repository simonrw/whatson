package config

import (
	"testing"

	"github.com/BurntSushi/toml"
)

func TestParseConfig(t *testing.T) {
	text := `
[[theatre]]
name = "albany"
active = true
root-url = "https://albanytheatre.co.uk/"
url = "https://albanytheatre.co.uk/whats-on/"
fetcher = "stdlib"
container-selector = "div.query_block_content"
link-selector = "h4 > a"
image-selector = "img"
title-selector = "h4 > a"
date-selector = ".show-date"
link-relative = true
`

	var currentConfig WhatsonConfig
	if _, err := toml.Decode(text, &currentConfig); err != nil {
		t.Errorf("error decoding")
	}

	if len(currentConfig.Theatres) != 1 {
		t.Errorf("incorrect number of theatres, found %d expected 1\n", len(currentConfig.Theatres))
	}

	th := currentConfig.Theatres[0]
	if th.ContainerSelector != "div.query_block_content" {
		t.Errorf("incorrect container selector\n")
	}

}
