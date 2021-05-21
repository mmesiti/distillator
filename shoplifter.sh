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
set_version_information $HIREP $SOMBRERO $SCRIPT_LOCATION
# 5
copy_sombrero_files $HIREP $SOMBRERO
# 6
clone_pycparser $PYCPARSER
# 7
analyse_callgraph $HIREP $PYCPARSER
# 8
copy_and_clean_selected_sources $HIREP $SOMBRERO
# 9
copy_makefiles $HIREP $SOMBRERO
# 10
copy_selected_headers used_headers.txt $SOMBRERO  all_unused_functions.txt
# 11
copy_additional_files $SCRIPT_LOCATION/additional_files_to_copy.txt $HIREP $SOMBRERO
# 12
clean_macros $SOMBRERO
# 13
package $SOMBRERO

echo "Finished."
