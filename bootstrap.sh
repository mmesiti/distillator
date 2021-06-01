#!/usr/bin/env bash
# This runs inside a docker container.
set -euo pipefail

git clone https://github.com/sa2c/shoplifter.git
mkdir build
(
    cd build
    ../shoplifter/shoplifter.sh
    cp ./sombrero.tar.gz /output/
)


