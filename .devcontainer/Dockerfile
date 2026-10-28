FROM golang:1.27.3-bookworm

ENV GOTOOLCHAIN=auto

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        jq \
    && rm -rf /var/lib/apt/lists/*

RUN go install golang.org/x/tools/gopls@latest \
    && go install github.com/go-delve/delve/cmd/dlv@latest \
    && go install golang.org/x/tools/cmd/goimports@latest \
    && go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest \
    && go install github.com/golangci/golines@latest

WORKDIR /workspace
