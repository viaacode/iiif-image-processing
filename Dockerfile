FROM python:3.9-slim

# Create a system user and group
RUN addgroup --system iiif && adduser --system iiif --ingroup iiif

WORKDIR /opt/iiif-image-processing

COPY --chown=iiif:iiif requirements.txt .

RUN pip install -r requirements.txt \
--extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-internal/simple \
--trusted-host do-prd-mvn-01.do.viaa.be --no-warn-script-location 

