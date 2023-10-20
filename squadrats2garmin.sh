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

if ! [[ -r "${CONFIG_FILE}" ]]; then
	usage
	exit 1
fi

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