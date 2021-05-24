#!/usr/bin/env bash
set -euo pipefail


# Local directories
HIREP=HiRep
SOMBRERO=sombrero
PYCPARSER=pycparser

# From https://stackoverflow.com/a/246128/3113564
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source $SCRIPT_LOCATION/remotes.sh

FFMODULE=$SCRIPT_LOCATION/files_and_functions
MACROMODULE=$SCRIPT_LOCATION/macros

export PYTHONPATH=$FFMODULE:$MACROMODULE


BOLD="\e[1;32m"
NORMAL="\e[0m"

get_commit_url() {
    local REPO="$1"
    local DIRNAME="$2"
    if get_commit_id_for_directory ${DIRNAME} >/dev/null; then
        echo ${REPO}/tree/$( get_commit_id_for_directory ${DIRNAME} )
    else
        echo ${REPO}
    fi
}
get_commit_id_for_directory() {
    local DIRNAME=$1
    local GIT_CMD="git -C ${DIRNAME} rev-parse --short HEAD"
    if ${GIT_CMD} >/dev/null 2>&1; then
        local ID=$( ${GIT_CMD} )
        if ! git -C ${DIRNAME} diff --exit-code >/dev/null; then
            local ID="${ID} (UNCOMMITTED CHANGES)"
            local RETVAL=1
        else
            local RETVAL=0
        fi
    else
        local ID="UNKNOWN"
        local RETVAL=2
    fi
    echo ${ID}
    return ${RETVAL}
}


# 1
clone_hirep(){
    local HIREP=$1
    echo -e "${BOLD}Cloning HiRep from $HIREP_REMOTE to $HIREP, on branch ${HIREP_REMOTE_BRANCH}${NORMAL}"
    git clone --depth=1 ${HIREP_REMOTE} --branch ${HIREP_REMOTE_BRANCH} ${HIREP} 
}
# 2
generate_headers(){
    local HIREP=$1
    echo -e "${BOLD}Preparing MkFlags${NORMAL}"
    local MKFLAGS=${HIREP}/Make/MkFlags
    echo -e "${BOLD}Back up of MkFlags${NORMAL}"
    cp $MKFLAGS $MKFLAGS.bu 
    grep -v "NG\|REPR\|GAUGE_GROUP" $MKFLAGS.bu > $MKFLAGS 

    write_headers(){
        local NG=$1
        local REPR=$2
        local GROUP=$3
        local NAME=$4
        echo -e "${BOLD}Writing headers for NG=$NG, REPR=$REPR, GROUP=$GROUP,  NAME=$NAME${NORMAL}"
        touch $MKFLAGS # To trigger ricompilation of write_repr
        (
            cd $HIREP/Include
            make NG=$NG REPR=$REPR GAUGE_GROUP=$GROUP
            echo -e mv suN.h $NAME.h 
            mv suN.h $NAME.h 
            echo -e mv suN_types.h ${NAME}_types.h
            mv suN_types.h ${NAME}_types.h
            echo -e mv suN_repr_func.h ${NAME}_repr_func.h
            mv suN_repr_func.h ${NAME}_repr_func.h
        ) 

    }

    write_headers 2 REPR_FUNDAMENTAL GAUGE_SUN su2
    write_headers 2 REPR_ADJOINT     GAUGE_SUN su2adj
    write_headers 3 REPR_FUNDAMENTAL GAUGE_SUN su3
    write_headers 3 REPR_SYMMETRIC   GAUGE_SUN su3sym
    write_headers 4 REPR_FUNDAMENTAL GAUGE_SPN sp4
    write_headers 4 REPR_ADJOINT     GAUGE_SPN sp4adj

}
# 3
clone_sombrero(){
    SOMBRERO=$1
    echo -e "${BOLD}Cloning Sombrero from ${SOMBRERO_REMOTE} to ${SOMBRERO}${NORMAL}"
    echo -e "${BOLD}(branch: ${SOMBRERO_REMOTE_BRANCH})${NORMAL}"
    git clone --depth=1 ${SOMBRERO_REMOTE} --branch ${SOMBRERO_REMOTE_BRANCH} ${SOMBRERO}
}
# 4
set_version_information(){
    portable_sed_in_place() {
        local EXPR="$1"
        local FILE="$2"
        local TMP_FILE="$( mktemp XXXXXXXX )"
        sed "${EXPR}" "${FILE}" > "${TMP_FILE}"
        mv "${TMP_FILE}" "${FILE}"
    }

    local HIREP="$1"
    local SOMBRERO="$2"
    local SHOPLIFTER="$3"

    local HIREP_COMMIT_ID="$4"
    local HIREP_URL="$5"

    local SOMBRERO_COMMIT_ID="$(get_commit_id_for_directory ${SOMBRERO})"
    local SHOPLIFTER_COMMIT_ID="$(get_commit_id_for_directory ${SHOPLIFTER})"
    local SOMBRERO_URL="$(get_commit_url https://github.com/sa2c/SOMBRERO ${SOMBRERO})"
    local SHOPLIFTER_URL="$(get_commit_url https://github.com/mmesiti/shoplifter ${SHOPLIFTER})"

    for FILE in ${SOMBRERO}/README.md ${SOMBRERO}/sombrero/sombrero.c; do
        portable_sed_in_place "s|{{hirep_commit}}|${HIREP_COMMIT_ID}|" ${FILE}
        portable_sed_in_place "s|{{sombrero_commit}}|${SOMBRERO_COMMIT_ID}|" ${FILE}
        portable_sed_in_place "s|{{shoplifter_commit}}|${SHOPLIFTER_COMMIT_ID}|" ${FILE}
        portable_sed_in_place "s|{{hirep_url}}|${HIREP_URL}|" ${FILE}
        portable_sed_in_place "s|{{sombrero_url}}|${SOMBRERO_URL}|" ${FILE}
        portable_sed_in_place "s|{{shoplifter_url}}|${SHOPLIFTER_URL}|" ${FILE}
    done
}
# 5
copy_sombrero_files(){
    local HIREP=$1
    local SOMBRERO=$2
    echo -e "${BOLD}Copying files from $SOMBRERO to $HIREP${NORMAL}"

    (
        set -o xtrace
        cp -r $SOMBRERO/sombrero $HIREP
        cp -r $SOMBRERO/sombrero $HIREP
        cp $SOMBRERO/Include/suN.h $HIREP/Include
        cp $SOMBRERO/Include/sombrero.h $HIREP/Include
        cp $SOMBRERO/Include/suN_repr_func.h $HIREP/Include
        cp $SOMBRERO/Include/libhr_defines_interface.h $HIREP/Include
        cp $SOMBRERO/Include/suN_types.h $HIREP/Include
    )
    # Processing LibHR files
    for FILE in $(find $SOMBRERO/LibHR -type f)
    do
        HIREPNAME=$(sed 's|'$SOMBRERO'|'$HIREP'|' <<< "$FILE")

        (
            set -o xtrace
            mkdir -p $(dirname $HIREPNAME)
            cp $FILE $HIREPNAME
        )
    done 

}
# 6
clone_pycparser(){
    local PYCPARSER=$1
    echo -e "${BOLD}Cloning $PYCPARSER${NORMAL}"
    git clone --depth=1 ${PYCPARSER_REMOTE} $PYCPARSER
}
# 7
analyse_callgraph(){
    local HIREP=$1
    local PYCPARSER=$2
    echo -e "${BOLD}Analysing Callgraph in $HIREP${NORMAL}"
    python3 $FFMODULE/main.py $FFMODULE/cpp_flags.yaml $HIREP $PYCPARSER
}
# 8
copy_and_clean_selected_sources(){
    # TODO: maybe use a flat directory instead?    
    local HIREP=$1
    local SOMBRERO=$2
    echo -e "${BOLD}Copying and cleaning selected sources from $HIREP to $SOMBRERO${NORMAL}"
    for FILE in $(cat all_used_sources.txt)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        mkdir -p $(dirname $NEWFILE)
        python3 $FFMODULE/filter_source.py $FILE $NEWFILE all_unused_functions.txt
    done

}
# 9
copy_makefiles(){
    # Since we're not using a flat directory,
    # we need to also copy the makefiles
    # only those which do not exist!
    local HIREP=$1
    local SOMBRERO=$2
    
    echo -e "${BOLD}Copying necessary Makefiles from $HIREP to $SOMBRERO${NORMAL}"
    for FILE in $(find $HIREP/LibHR -name Makefile)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        if [ -d $(dirname $NEWFILE) ]
        then
            if [ ! -f $NEWFILE ]
            then
                (
                    set -o xtrace
                    echo -e $(dirname $NEWFILE)
                    cp $FILE $NEWFILE
                )
            fi
        fi
    done
}
# 10
copy_selected_headers(){
    local FILELIST=$1
    local SOMBRERO=$2
    local UNUSED_FUNCTIONS=$3
    echo -e "${BOLD}Copying necessary Makefiles from $HIREP to $SOMBRERO${NORMAL}"
    for FILE in $(cat $FILELIST)
    do
        echo -e $FILE
        NEWFILE=$SOMBRERO/Include/$(basename $FILE)
        python3 $FFMODULE/filter_header.py $FILE $NEWFILE $UNUSED_FUNCTIONS
    done 
}
# 11
copy_additional_files(){
    local FILELIST=$1
    local HIREP=$2
    local SOMBRERO=$3
    echo -e "${BOLD}Copying additional flies from $HIREP to $SOMBRERO${NORMAL}"
    for FILE in $(cat $FILELIST)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        (
            set -o xtrace
            mkdir -p $(dirname $NEWFILE)
            cp $FILE $NEWFILE
        )
    done
}
# 12
clean_macros(){
    local SOMBRERO=$1
    echo -e "${BOLD}Cleaning macros in $SOMBRERO${NORMAL}"
    $MACROMODULE/replace_macros.sh $SOMBRERO
}

# 13
package(){
    local SOMBRERO=$1
    local OUTPUT=sombrero.tar.gz
    echo -e "${BOLD}Packaging all relevant files in $SOMBRERO into $OUTPUT${NORMAL}"
    find $SOMBRERO -type f | grep -v '.git' | xargs tar -cvf sombrero.tar.gz
}
