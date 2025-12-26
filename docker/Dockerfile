# syntax=docker/dockerfile:1
FROM eclipse-temurin:25-jre-noble

RUN mkdir "/output"
VOLUME /output

ARG MKGMAP_VERSION=r4923
ARG SQUADRATS2GARMIN_VERSION

RUN apt-get update && apt-get install --yes curl

# put mkgmap in /mkgmap and install a script to run it
ENV MKGMAP_HOME=/opt/mkgmap
RUN mkdir -p $MKGMAP_HOME
RUN curl -LsSf https://www.mkgmap.org.uk/download/mkgmap-$MKGMAP_VERSION.tar.gz | tar zx --strip-components=1 -C $MKGMAP_HOME
COPY mkgmap-log.cfg $MKGMAP_HOME/
COPY --chmod=755 mkgmap.sh /usr/local/bin/mkgmap

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# squadrats2garmin
ENV SQUADRATS2GARMIN_WHL=/opt/squadrats2garmin/squadrats2garmin-$SQUADRATS2GARMIN_VERSION-py3-none-any.whl
ADD squadrats2garmin-$SQUADRATS2GARMIN_VERSION-py3-none-any.whl $SQUADRATS2GARMIN_WHL
# download all requirements - TODO: find a nicer solution
RUN /root/.local/bin/uv run --with "${SQUADRATS2GARMIN_WHL}" visited --help

#LABEL authors="kbrazulewicz"
ENV SQUADRATS_USERID=P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1
ENV SQUADRATS2GARMIN_VERBOSE=

COPY --chmod=755 entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]