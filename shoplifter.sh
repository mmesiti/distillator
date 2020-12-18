#!/usr/bin/env bash
set -euo pipefail
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SCRIPT_LOCATION/lib.sh

# 1
clone_hirep $HIREP
# 2
generate_headers $HIREP
# 3
clone_sombrero $SOMBRERO
# 4
copy_sombrero_files $HIREP $SOMBRERO  
# 5
clone_pycparser $PYCPARSER
# 6
analyse_callgraph $HIREP $PYCPARSER
# 7 
copy_and_clean_selected_sources $HIREP $SOMBRERO  
# 8
copy_makefiles $HIREP $SOMBRERO  
# 9
copy_selected_headers used_headers.txt $SOMBRERO  all_unused_functions.txt
#10 
copy_additional_files $SCRIPT_LOCATION/additional_files_to_copy.txt $HIREP $SOMBRERO
#11
clean_macros $SOMBRERO
#12
package $SOMBRERO
