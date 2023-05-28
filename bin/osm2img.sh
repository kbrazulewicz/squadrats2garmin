#! /bin/bash

if [[ $# -ne 2 ]]; then
    exit
fi

id=$1
configFile=$2
outputDir=tmp

while read -r k; read -r v;
do
    declare "$k"="$v"
done < <(jq -r "(.jobs[] | select(.id == \"${id}\") | (\"polyFile\", .poly, \"osmFile\", .osm, (.mkgmap | to_entries | .[] | (.key, .value))))" ${configFile})

# name substitution in osmFile and imgFile
polyFileStem=$(basename "${polyFile%.*}")

osmFile=${osmFile/\{name\}/$polyFileStem}
imgFile=${imgFile/\{name\}/$polyFileStem}

# build options for mkgmap
MKGMAP_OPTS=("--mapname=${mapName}" "--description=${description}")
MKGMAP_OPTS+=("--family-id=${familyId}" "--family-name=${familyName}")
MKGMAP_OPTS+=("--product-id=${productId}")
MKGMAP_OPTS+=("--series-name=${seriesName}" "--area-name=${areaName}")
MKGMAP_OPTS+=("--transparent")
if [ ! -z "${countryName}" ]; then
    MKGMAP_OPTS+=("--country-name=${countryName}" "--country-abbr=${countryAbbr}")
fi
if [ ! -z "${regionName}" ]; then
    MKGMAP_OPTS+=("--region-name=${regionName}" "--region-abbr=${regionAbbr}")
fi
MKGMAP_OPTS+=("--output-dir=${outputDir}")
MKGMAP_OPTS+=("--gmapsupp" "${osmFile}")

echo Converting ${osmFile}
mkdir -p ${outputDir}
mkgmap "${MKGMAP_OPTS[@]}"

if [[ -r "${outputDir}/gmapsupp.img" ]]; then
    mkdir -p $(dirname "$imgFile")
    mv ${outputDir}/gmapsupp.img ${imgFile}
    rm ${outputDir}/${mapName}.img ${outputDir}/ovm_${mapName}.img ${outputDir}/osmmap.*
fi
