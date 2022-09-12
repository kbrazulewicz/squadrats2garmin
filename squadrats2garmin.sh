#! /bin/bash

CONFIG_DIR=config
OUTPUT_DIR=output
MKGMAP_DIR=mkgmap-r4905

FID=9628
FNAME="Squadrats"

function generateOsm() {
	echo Generating ${2}
	python3 generate-osm.py ${1} > ${2}
}

# init
mkdir -p ${OUTPUT_DIR}

# cleanup
rm -rf ${OUTPUT_DIR}/*

generateOsm ${CONFIG_DIR}/squadrats-poland.json ${OUTPUT_DIR}/squadrats-poland.osm
generateOsm ${CONFIG_DIR}/squadratinhos-tricity.json ${OUTPUT_DIR}/squadratinhos-tricity.osm

#rem generate Squadrats image for Poland
PID=1
DESC="Squadrats Poland"
FILE=squadrats-poland
MAPNAME=${FID}000${PID}
OSM_FILE=${OUTPUT_DIR}/${FILE}.osm
IMG_FILE=${OUTPUT_DIR}/${FILE}.img
java -jar ${MKGMAP_DIR}/mkgmap.jar --family-id=${FID} --family-name="${FNAME}" --product-id=${PID} --series-name="${DESC}" --description="${DESC}" --transparent --mapname=${MAPNAME} --output-dir="${OUTPUT_DIR}" --gmapsupp "${OSM_FILE}"

mv ${OUTPUT_DIR}/gmapsupp.img ${IMG_FILE}
rm ${OUTPUT_DIR}/${MAPNAME}.img ${OUTPUT_DIR}/ovm_${MAPNAME}.img ${OUTPUT_DIR}/osmmap.*
#gmt -i ${IMG_FILE}


PID=2
DESC="Squadratinhos Tricity"
FILE=squadratinhos-tricity
MAPNAME=${FID}000${PID}
OSM_FILE=${OUTPUT_DIR}/${FILE}.osm
IMG_FILE=${OUTPUT_DIR}/${FILE}.img
java -jar ${MKGMAP_DIR}/mkgmap.jar --family-id=${FID} --family-name="${FNAME}" --product-id=${PID} --series-name="${DESC}" --description="${DESC}" --transparent --mapname=${MAPNAME} --output-dir="${OUTPUT_DIR}" --gmapsupp "${OSM_FILE}"

mv ${OUTPUT_DIR}/gmapsupp.img ${IMG_FILE}
rm ${OUTPUT_DIR}/${MAPNAME}.img ${OUTPUT_DIR}/ovm_${MAPNAME}.img ${OUTPUT_DIR}/osmmap.*
#gmt -i ${IMG_FILE}
