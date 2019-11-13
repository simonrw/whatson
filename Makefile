all: dist/server

dist/server: cmd/server/main.go
	go build -o $@ $<

.PHONY: clean
clean:
	@rm -rf dist
