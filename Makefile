BASE_TAG := srwalker101/whatson

all: build-ingest build-web

build-ingest:
	docker build -t ${BASE_TAG}-ingest:latest -f Dockerfile.ingest .

build-web:
	docker build -t ${BASE_TAG}-web:latest -f Dockerfile.webapp .

push-ingest: build-ingest
	docker push ${BASE_TAG}-ingest

push-web: build-web
	docker push ${BASE_TAG}-web

provision:
	bash -c "source .env && ansible-playbook -i hosts --ask-become-pass provisioning/main.yml --tags current"

.PHONY: build-ingest build-web push-ingest push-web provision
