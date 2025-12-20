#! /bin/sh

exec java -Xms1g -Xmx1g -Dlog.config="${HOME}/lib/mkgmap-log.cfg" -jar /mkgmap/mkgmap.jar "$@"