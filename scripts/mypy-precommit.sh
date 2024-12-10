#!/usr/bin/env bash

function log() {
    >&2 echo "${@}"
}

# shellcheck disable=SC2016,SC2207
PACKAGE_PATHS=($(git diff --name-only --cached --diff-filter=ACMR \
                    | tr "/" " " \
                    | awk '{print $1}' \
                    | xargs -l sh -c 'find "$0" -type f -name pyproject.toml -printf "%h\n"'))

[ ${#PACKAGE_PATHS[@]} -gt 0 ] || { exit 0; }

FAILED=()
for PACKAGE_PATH in "${PACKAGE_PATHS[@]}"; do
    PACKAGE_NAME=$(basename "${PACKAGE_PATH}")
    pushd "${PACKAGE_PATH}" >/dev/null ||  { FAILED+=("${PACKAGE_NAME}"); continue; }

    log "Running mypy $PWD"
    poetry run "mypy" "." || { FAILED+=("${PACKAGE_NAME}"); }

    popd >/dev/null || { continue; }
done

if [ ${#FAILED[@]} -gt 0 ]; then
    log "The following packages failed to be checked: ${FAILED[*]}"
    exit 1
fi
