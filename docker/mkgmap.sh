#! /bin/sh
# wrapper script to run mkgmap

exec java -Xms1g -Xmx1g -Dlog.config="${MKGMAP_HOME}/mkgmap-log.cfg" -jar "${MKGMAP_HOME}/mkgmap.jar" "$@"