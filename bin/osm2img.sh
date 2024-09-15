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

# default mkgmap style and Garmin TYP
styleFile="${styleFile:-style/squadrats-default.style}"
typFile="${typFile:-typ/squadrats.typ.txt}"

# build options for mkgmap
MKGMAP_OPTS=mkgmap.config
rm -f $MKGMAP_OPTS
echo "gmapsupp" >> $MKGMAP_OPTS
echo "latin1" >> $MKGMAP_OPTS
echo "transparent" >> $MKGMAP_OPTS
echo "mapname=${mapName}" >> $MKGMAP_OPTS
echo "description=${description}" >> $MKGMAP_OPTS
echo "family-id=${familyId}" >> $MKGMAP_OPTS
echo "family-name=${familyName}" >> $MKGMAP_OPTS
echo "product-id=${productId}" >> $MKGMAP_OPTS
echo "series-name=${seriesName}" >> $MKGMAP_OPTS
echo "area-name=${areaName}" >> $MKGMAP_OPTS
if [ ! -z "${countryName}" ]; then
    echo "country-name=${countryName}" >> $MKGMAP_OPTS
    echo "country-abbr=${countryAbbr}" >> $MKGMAP_OPTS
fi
if [ ! -z "${regionName}" ]; then
    echo "region-name=${regionName}" >> $MKGMAP_OPTS
    echo "region-abbr=${regionAbbr}" >> $MKGMAP_OPTS
fi
echo "output-dir=${outputDir}" >> $MKGMAP_OPTS
echo "style-file=${styleFile}" >> $MKGMAP_OPTS
echo "input-file=${typFile}" >> $MKGMAP_OPTS
echo "input-file=${osmFile}" >> $MKGMAP_OPTS

echo Converting ${osmFile}
mkdir -p ${outputDir}
mkgmap --read-config=${MKGMAP_OPTS}

if [[ -r "${outputDir}/gmapsupp.img" ]]; then
    mkdir -p $(dirname "$imgFile")
    mv ${outputDir}/gmapsupp.img ${imgFile}
    rm ${outputDir}/*
fi
