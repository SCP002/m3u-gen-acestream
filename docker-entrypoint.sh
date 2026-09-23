#!/bin/sh
set -eu

if [ -z "${INTERVAL:-}" ]; then
    exec m3u-gen-acestream "$@"
fi

trap 'exit 0' INT TERM

while :; do
    m3u-gen-acestream "$@" || true
    printf '\nNext run in %s\n\n' "${INTERVAL}"
    sleep "${INTERVAL}" &
    wait $!
done
