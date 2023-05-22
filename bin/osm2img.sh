#! /bin/bash

outputDir=output

while [ $# -gt 0 ]; do
    if [[ $1 == "--"* ]]; then
        v="${1/--/}"
        declare "$v"="$2"
        shift
    fi
    shift
done

MKGMAP_OPTS=("--mapname=${mapname}" "--description=${description}")
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

mkgmap "${MKGMAP_OPTS[@]}"

mkdir -p $(dirname "$imgFile")
mv ${outputDir}/gmapsupp.img ${imgFile}
rm ${outputDir}/${mapname}.img ${outputDir}/ovm_${mapname}.img ${outputDir}/osmmap.*