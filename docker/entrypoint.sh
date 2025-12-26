#! /bin/bash

OUTPUT="/output/visited-squadrats.img"

# import uv's setup
source ~/.local/bin/env

# shellcheck disable=SC2090
# shellcheck disable=SC2086
uv run --with "${SQUADRATS2GARMIN_WHL}" visited ${SQUADRATS2GARMIN_VERBOSE:+--verbose} -u "${SQUADRATS_USERID}" -o "${OUTPUT}"