# https://docs.docker.com/develop/develop-images/multistage-build/
FROM eclipse-temurin:25-jre-noble

ARG MKGMAP_VERSION=r4923

WORKDIR /build
RUN apt-get update && apt-get install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN curl -s -L https://www.mkgmap.org.uk/download/mkgmap-$MKGMAP_VERSION.tar.gz | tar -xz && mv mkgmap-$MKGMAP_VERSION mkgmap

#LABEL authors="kbrazulewicz"

ENTRYPOINT ["top", "-b"]