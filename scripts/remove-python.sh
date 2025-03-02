#!/usr/bin/env bash

# Removes old conda, poetry and micromamba installations

PATHS_TO_REMOVE=(
    ~/.cache/conda
    ~/.cache/pip
    ~/.cache/pypoetry
    ~/.cache/uv
    ~/.local/bin/micromamba
    ~/micromamba
)

function log() {
    >&2 echo "$(date '+%Y-%m-%d %H:%M:%S') ${*}"
}

set -euo pipefail

for PATH_TO_REMOVE in "${PATHS_TO_REMOVE[@]}"
do
    if [ -e "${PATH_TO_REMOVE}" ]; then
        log "rm -rf ${PATH_TO_REMOVE}"
        rm -rf "${PATH_TO_REMOVE}"
    fi
done
