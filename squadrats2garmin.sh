#! /bin/bash

function usage {
    echo "Usage: $0 [-h] <config-file>"
}

while getopts ":h:" o; do
    case "${o}" in
        *)
            usage
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

CONFIG_FILE=${1:-config/squadrats2osm.json}
OUTPUT_DIR=output
MKGMAP_OPTS="${OUTPUT_DIR}/mkgmap.conf"

if ! [[ -r "${CONFIG_FILE}" ]]; then
    usage
    exit 1
fi

IMG_FILE=$(jq -r '.output' "${CONFIG_FILE}")

# init
mkdir -p ${OUTPUT_DIR}

# cleanup
rm -rf ${OUTPUT_DIR:?}/*

# generate OSM files
python3 squadrats2osm/squadrats2osm.py "${CONFIG_FILE}"

# generate Garmin IMG file
mkgmap --read-config="${MKGMAP_OPTS}"

if [[ -r "${OUTPUT_DIR}/gmapsupp.img" ]]; then
    mkdir -p "$(dirname "${IMG_FILE}")"
    mv ${OUTPUT_DIR}/gmapsupp.img "${IMG_FILE}"
    rm ${OUTPUT_DIR}/*
fi