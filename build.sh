#!/bin/bash

project_name="m3u-gen-acestream"
build_path="build"
version="v2.2.2"

command -v go > /dev/null || { echo "go not found in PATH" >&2; exit 1; }

mkdir -p "$build_path"

for target in $(go tool dist list); do
    os=${target%/*}
    arch=${target#*/}
    ext=""
    [[ $os == "windows" ]] && ext=".exe"
    [[ $arch == "wasm" ]] && ext=".wasm"

    echo "Building for $os / $arch"
    GOOS=$os GOARCH=$arch go build -ldflags "-X m3u-gen-acestream/version.Version=${version}" -o "${build_path}/${project_name}-${os}-${arch}${ext}" .
done
