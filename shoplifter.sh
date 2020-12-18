#!/usr/bin/env bash
set -euo pipefail
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SCRIPT_LOCATION/lib.sh

# 1
clone_hirep
# 2
generate_headers
# 3
clone_sombrero
# 4
copy_sombrero_files
# 5
clone_pycparser
# 6
analyse_callgraph
# 7 
copy_and_clean_selected_sources 
# 8
copy_makefiles
# 9
copy_selected_headers 
#10 
copy_additional_files 
#11
clean_macros

