#!/bin/bash

project_name="m3u-gen-acestream"
build_path="build"
version="v3.0.0"

command -v go > /dev/null || { echo "go not found in PATH" >&2; exit 1; }

mkdir -p "$build_path"

for target in $(go tool dist list); do
    os=${target%/*}
    arch=${target#*/}
    ext=""
    [[ $os == "windows" ]] && ext=".exe"
    [[ $arch == "wasm" ]] && ext=".wasm"

    echo "Building for $os / $arch"
    CGO_ENABLED=0 GOOS=$os GOARCH=$arch go build -trimpath -ldflags "-X ${project_name}/version.Version=${version}" -o "${build_path}/${project_name}-${os}-${arch}${ext}" .
done
