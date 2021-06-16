#!/usr/bin/env bash
# This runs inside a docker container.
set -euo pipefail

git clone https://github.com/sa2c/shoplifter.git
mkdir build
(
    cd build
    ../shoplifter/shoplifter.sh
    (
    cd sombrero
    make
    ./sombrero.sh -n 2 -p 2x1x1x1 -l 8x8x8x8
    )
    cp ./sombrero.tar.gz /output/
)


