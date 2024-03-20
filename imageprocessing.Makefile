.ONESHELL:
SHELL = /bin/bash
IMAGE_NAME = iiif/iiif-image-processing
REGISTRY = default-route-openshift-image-registry.meemoo2-2bc857e5f10eb63ab790a3a1d19a696c-i000.eu-de.containers.appdomain.cloud

check-env:
ifndef ENV
        $(error ENV is undefined)
endif

test:
        echo Testing not implemented

pull: check-env
        docker pull ${REGISTRY}/${IMAGE_NAME}:${ENV}

run:  check-env
        docker run --name=imageserver-watcher -d -v /export/home\:/export/home -v /opt/image-processing-workfolder\:/opt/image-processing-workfolder -v /opt/kakadu\:/opt/kakadu --rm --env-file=.env --user 1002\:1002 ${REGISTRY}/${IMAGE_NAME}:${ENV}

restart: check-env
        docker ps -q --filter "name=imageserver-watcher" | xargs docker stop;
        docker run -d --name=imageserver-watcher -v /export/home\:/export/home --rm --env-file=.env --user 1002\:1002 ${REGISTRY}/${IMAGE_NAME}:${ENV}

