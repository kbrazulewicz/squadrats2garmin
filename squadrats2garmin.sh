#! /bin/bash

CONFIG_DIR=config
OUTPUT_DIR=output
DIST_DIR=dist

# 9 + https://en.wikipedia.org/wiki/ISO_3166-1 code for Poland
familyId=9616
familyName="Squadrats Poland"

# init
mkdir -p ${OUTPUT_DIR}

# cleanup
# rm -rf ${OUTPUT_DIR}/*

# python3 squadrats2osm/squadrats2osm.py ${CONFIG_DIR}/squadrats2osm.json

bin/osm2img.sh --mapname "${familyId}0001" --description "europe/poland Squadrats" \
	--familyId ${familyId} --familyName "${familyName}" \
	--productId 1 \
	--seriesName "Squadrats" --areaName "europe/poland" \
	--countryName "Poland" --countryAbbr "PL" \
	--osmFile ${OUTPUT_DIR}/europe/squadrats-PL-poland.osm \
	--imgFile ${DIST_DIR}/europe/squadrats-PL-poland.img 

bin/osm2img.sh --mapname "${familyId}0101" --description "europe/poland Squadratinhos" \
	--familyId ${familyId} --familyName "${familyName}" \
	--productId 101 \
	--seriesName "Squadrats" --areaName "europe/poland" \
	--countryName "Poland" --countryAbbr "PL" \
	--osmFile ${OUTPUT_DIR}/europe/squadratinhos-PL-poland.osm \
	--imgFile ${DIST_DIR}/europe/squadratinhos-PL-poland.img 

bin/osm2img.sh --mapname "${familyId}0122" --description "europe/poland/pomorskie Squadratinhos" \
	--familyId ${familyId} --familyName "${familyName}" \
	--productId 122 \
	--seriesName "Squadrats" --areaName "europe/poland" \
	--countryName "Poland" --countryAbbr "PL" \
	--regionName "Pomerania" --regionAbbr "PM" \
	--osmFile ${OUTPUT_DIR}/europe/poland/squadratinhos-PL-22-pomorskie.osm \
	--imgFile ${DIST_DIR}/europe/poland/squadratinhos-PL-22-pomorskie.img 
