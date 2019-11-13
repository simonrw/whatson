GOFILES := $(wildcard common/*/*.go)

all: dist/server

.PHONY: runserver
runserver: dist/server
	$<

dist/server: cmd/server/main.go ${GOFILES}
	go build -o $@ $<

.PHONY: clean
clean:
	@rm -rf dist

.PHONY: test
test:
	go test ./...
