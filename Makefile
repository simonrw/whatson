BASE_TAG := srwalker101/whatson

.PHONY: all
all: build-ingest build-web

.PHONY: build-ingest
build-ingest:
	docker build -t ${BASE_TAG}-ingest:latest -f Dockerfile.ingest .

.PHONY: build-web
build-web:
	docker build -t ${BASE_TAG}-web:latest -f Dockerfile.webapp .

.PHONY: push-ingest
push-ingest: build-ingest
	docker push ${BASE_TAG}-ingest

.PHONY: push-web
push-web: build-web
	docker push ${BASE_TAG}-web

.PHONY: push
push: push-web push-ingest

.PHONY: provision
provision:
	bash -c "source .env && ansible-playbook -i hosts --ask-become-pass provisioning/main.yml"

.PHONY: devserver
devserver:
	FLASK_APP=whatson.webapp FLASK_DEBUG=1 flask run --port 5000
