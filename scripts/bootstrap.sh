#!/usr/bin/env bash

SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if grep -q poetry "pyproject.toml" >/dev/null 2>&1; then
    echo "Installing dependencies for $(basename "$(pwd)")..."
    exec "${SCRIPT_PATH}/console.sh" poetry install
fi

>&2 echo "No poetry dependencies available for $(basename "$(pwd)")."
exit 1
