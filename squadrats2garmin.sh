#! /bin/bash

CONFIG_DIR=config
OUTPUT_DIR=output

FID=9628
FNAME="Squadrats"

# init
mkdir -p ${OUTPUT_DIR}

# cleanup
rm -rf ${OUTPUT_DIR}/*

python3 squadrats2osm/squadrats2osm.py ${CONFIG_DIR}/squadrats2osm.json

#rem generate Squadrats image for Poland
PID=1
DESC="Squadrats Poland"
MAPNAME=${FID}000${PID}
OSM_FILE=${OUTPUT_DIR}/europe/poland_14.osm
IMG_FILE=${OUTPUT_DIR}/europe/squadrats_poland.img
mkgmap --mapname=${MAPNAME} --description="${DESC}" \
	--family-id=${FID} --family-name="${FNAME}" \
	--product-id=${PID} --series-name="${DESC}" --transparent \
	--country-name="Poland" --country-abbr="PL" \
	--output-dir="${OUTPUT_DIR}" \
	--gmapsupp \
	"${OSM_FILE}"

mv ${OUTPUT_DIR}/gmapsupp.img ${IMG_FILE}
rm ${OUTPUT_DIR}/${MAPNAME}.img ${OUTPUT_DIR}/ovm_${MAPNAME}.img ${OUTPUT_DIR}/osmmap.*
#gmt -i ${IMG_FILE}


PID=2
DESC="Squadratinhos Pomorskie"
MAPNAME=${FID}000${PID}
OSM_FILE=${OUTPUT_DIR}/europe/poland/pomorskie_17.osm
IMG_FILE=${OUTPUT_DIR}/europe/poland/squadratinhos_pl_pomorskie.img
mkgmap --mapname=${MAPNAME} --description="${DESC}" \
	--family-id=${FID} --family-name="${FNAME}" \
	--product-id=${OSM_ID} --series-name="${DESC}" --transparent \
	--country-name="Poland" --country-abbr="PL" \
	--region-name="Pomerania" --region-abbr="PM" \
	--output-dir="${OUTPUT_DIR}" \
	--gmapsupp \
	"${OSM_FILE}"

mv ${OUTPUT_DIR}/gmapsupp.img ${IMG_FILE}
rm ${OUTPUT_DIR}/${MAPNAME}.img ${OUTPUT_DIR}/ovm_${MAPNAME}.img ${OUTPUT_DIR}/osmmap.*
#gmt -i ${IMG_FILE}
