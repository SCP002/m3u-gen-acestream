FROM golang:1.27-alpine AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .

ARG VERSION=dev
RUN CGO_ENABLED=0 go build -trimpath \
    -ldflags "-X m3u-gen-acestream/version.Version=${VERSION}" \
    -o /m3u-gen-acestream .

FROM alpine:3.23

RUN apk add --no-cache ca-certificates tzdata

COPY --from=builder /m3u-gen-acestream /usr/local/bin/m3u-gen-acestream
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

WORKDIR /data

CMD ["--cfgPath", "/data/config/m3u-gen-acestream.yaml"]

ENTRYPOINT ["docker-entrypoint.sh"]
