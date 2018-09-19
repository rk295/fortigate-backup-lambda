#!/usr/bin/env bash
#
# Hacky script to zip up a python program in a format useable by AWS Lambda.
#
# Optionally looks for the following environment variables:
#
# * ZIP_NAME        - Name of the zip file to create, defaults to 'rk-test.zip'
# * PYTHON_SOURCE   - Name of the python main python script to include in the
#                     package, defaults to 'simple.py'
# * VIRTUAL_ENV_DIR - Path to the python virtual environment, defaults to ./venv
#
set -euo pipefail

cd "${0%/*}" || exit 1
baseDir=$(pwd)

: ${ZIP_NAME:="fortigate-backup.zip"}
: ${PYTHON_SOURCE:="forti-backup.py"}
: ${VIRTUAL_ENV_DIR:="venv"}

cd "$baseDir" || exit 1

echo "Removing old zip ($ZIP_NAME)"
rm -f "$ZIP_NAME"

# Running in a subshell, because I don't like cd'ing from the main body of a
# script.
(
    echo "Adding site packages"
    # Hardcoded to assume your python virtual environment is under `venv`, not sure
    # how else I could figure this out.
    cd "$VIRTUAL_ENV_DIR/lib/python2.7/site-packages/" || exit 1
    zip -qr9 "$baseDir/$ZIP_NAME" .
)

echo "Adding $PYTHON_SOURCE"
zip -qr9 "$baseDir/$ZIP_NAME" "$PYTHON_SOURCE"
