GOFILES := $(wildcard internal/*/*.go)

all: dist/ingest

.PHONY: runserver
runserver: dist/server
	@$<

.PHONY: runingest
runingest: dist/ingest
	@$<

dist/%: cmd/%/main.go ${GOFILES}
	go build -o $@ $<

.PHONY: clean
clean:
	@rm -rf dist

.PHONY: test
test:
	go test ./...
