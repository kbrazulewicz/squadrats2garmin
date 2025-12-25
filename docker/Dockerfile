# syntax=docker/dockerfile:1
FROM scratch AS src
ARG MKGMAP_VERSION=r4923
ARG SQUADRATS2GARMIN_VERSION

ADD --unpack=false https://www.mkgmap.org.uk/download/mkgmap-$MKGMAP_VERSION.tar.gz /mkgmap.tar.gz
ADD --chmod=755 https://astral.sh/uv/install.sh /uv-install.sh
ADD --unpack=false squadrats2garmin-$SQUADRATS2GARMIN_VERSION.tar.gz /squadrats2garmin.tar.gz

#
FROM alpine AS unpack
# unpack mkgmap, strip 1 directory level
RUN --mount=from=src,target=/src <<EOF
mkdir -p /mkgmap
tar --strip-components=1 -xzf /src/mkgmap.tar.gz -C /mkgmap
EOF
COPY mkgmap-log.cfg /mkgmap

# unpack squadrats2garmin, strip 1 directory level
RUN --mount=from=src,target=/src <<EOF
mkdir -p /squadrats2garmin
tar --strip-components=1 -xzf /src/squadrats2garmin.tar.gz -C /squadrats2garmin
EOF


FROM eclipse-temurin:25-jre-noble
RUN apt-get update && apt-get install --yes curl

# put mkgmap in /mkgmap and install a script to run it
ENV MKGMAP_HOME=/opt/mkgmap
COPY --from=unpack /mkgmap $MKGMAP_HOME
COPY --chmod=755 mkgmap.sh /usr/local/bin/mkgmap

# squadrats2garmin
ENV SQUADRATS2GARMIN_HOME=/opt/squadrats2garmin
COPY --from=unpack /squadrats2garmin $SQUADRATS2GARMIN_HOME

# install uv
RUN --mount=from=src,target=/src <<EOF
/src/uv-install.sh
EOF
RUN /root/.local/bin/uv sync --directory $SQUADRATS2GARMIN_HOME


#LABEL authors="kbrazulewicz"
ENV SQUADRATS_USERID=P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1
#ENTRYPOINT ["uv", "--directory", "$SQUADRATS2GARMIN_HOME", "run", "visited", "-u", "$SQUADRATS_USERID", "-o", "visited-squadrats.img"]