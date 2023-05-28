#! /bin/bash

CONFIG_FILE=config/squadrats2osm.json
OUTPUT_DIR=output
DIST_DIR=dist

# 9 + https://en.wikipedia.org/wiki/ISO_3166-1 code for Poland
familyId=9616
familyName="Squadrats Poland"

# init
mkdir -p ${OUTPUT_DIR}

# cleanup
rm -rf ${OUTPUT_DIR}/*

# generate OSM files
python3 squadrats2osm/squadrats2osm.py ${CONFIG_FILE}

# generate Garmin IMG files
for id in `jq -r '.jobs[].id' ${CONFIG_FILE}`; do
	bin/osm2img.sh ${id} ${CONFIG_FILE}
done