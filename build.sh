#!/bin/bash

project_name="m3u_gen_acestream"
build_path="build"

command -v go > /dev/null || { echo "go not found in PATH" >&2; exit 1; }

mkdir -p "$build_path"

for target in $(go tool dist list); do
    os=${target%/*}
    arch=${target#*/}
    ext=""
    [[ $os == "windows" ]] && ext=".exe"
    [[ $arch == "wasm" ]] && ext=".wasm"

    echo "Building for $os / $arch"
    GOOS=$os GOARCH=$arch go build -o "${build_path}/${project_name}_${os}_${arch}${ext}" "${project_name}.go"
done
