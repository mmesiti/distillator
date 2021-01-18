#!/usr/bin/env bash
# This runs inside a docker container.
set -euo pipefail

git clone https://github.com/mmesiti/shoplifter.git
mkdir build
(
    cd build
    ../shoplifter/shoplifter.sh
    cp ./sombrero.tar.gz /output/
)


