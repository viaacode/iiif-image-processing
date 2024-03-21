.ONESHELL:
SHELL = /bin/bash
REGISTRY = default-route-openshift-image-registry.meemoo2-2bc857e5f10eb63ab790a3a1d19a696c-i000.eu-de.containers.appdomain.cloud
IMAGE_NAME = iiif/iiif-image-processing
check-env:
ifndef ENV
	$(error ENV is undefined)
endif

.PHONY: all test

test:
	pip install -r requirements.txt --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be
	pip install -r requirements-test.txt
	pytest -vvv --cov=./app --junit-xml=./tests/test_results.xml

run: check-env
	docker run -it -v /export/home:/export/home --env-file=.env --user 1002:1002 ${REGISTRY}/${IMAGE_NAME}:$${ENV}
