# syntax=docker/dockerfile:1

FROM golang:1.27.3-alpine AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .

# Version is taken from build.sh unless set explicitly.
ARG VERSION
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    version="${VERSION:-$(sed -n 's/^version="\(.*\)"$/\1/p' build.sh)}" \
    && CGO_ENABLED=0 go build -trimpath \
        -ldflags "-s -w -X m3u-gen-acestream/version.Version=${version}" \
        -o /m3u-gen-acestream .

FROM alpine:3.23

RUN apk add --no-cache ca-certificates tzdata

COPY --from=builder /m3u-gen-acestream /usr/local/bin/m3u-gen-acestream
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

WORKDIR /data

CMD ["--cfgPath", "/data/config/m3u-gen-acestream.yaml"]

ENTRYPOINT ["docker-entrypoint.sh"]
