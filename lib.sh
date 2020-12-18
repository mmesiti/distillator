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

# 1
clone_hirep(){
    local HIREP=$1
    git clone --depth=1 ${HIREP_REMOTE} --branch ${HIREP_REMOTE_BRANCH} ${HIREP} 
}
# 2
generate_headers(){
    local HIREP=$1
    echo "Preparing MkFlags"
    local MKFLAGS=${HIREP}/Make/MkFlags
    cp $MKFLAGS $MKFLAGS.bu 
    grep -v "NG\|REPR\|GAUGE_GROUP" $MKFLAGS.bu > $MKFLAGS 

    write_headers(){
        local NG=$1
        local REPR=$2
        local GROUP=$3
        local NAME=$4
        local OLDDIR=$(pwd)
        echo Writing headers
        touch $MKFLAGS # To trigger ricompilation of write_repr
        (
            cd $HIREP/Include
            make NG=$NG REPR=$REPR GAUGE_GROUP=$GROUP
            echo mv suN.h $NAME.h 
            mv suN.h $NAME.h 
            echo mv suN_types.h ${NAME}_types.h
            mv suN_types.h ${NAME}_types.h
            echo mv suN_repr_func.h ${NAME}_repr_func.h
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
    git clone --depth=1 ${SOMBRERO_REMOTE} --branch ${SOMBRERO_REMOTE_BRANCH} ${SOMBRERO}
}
# 4
copy_sombrero_files(){
    local HIREP=$1
    local SOMBRERO=$2

    cp -r $SOMBRERO/sombrero $HIREP
    cp $SOMBRERO/Include/suN.h $HIREP/Include
    cp $SOMBRERO/Include/sombrero.h $HIREP/Include
    cp $SOMBRERO/Include/suN_repr_func.h $HIREP/Include
    cp $SOMBRERO/Include/libhr_defines_interface.h $HIREP/Include
    cp $SOMBRERO/Include/suN_types.h $HIREP/Include

    # Processing LibHR files
    for FILE in $(find $SOMBRERO/LibHR -type f)
    do
        HIREPNAME=$(sed 's|'$SOMBRERO'|'$HIREP'|' <<< "$FILE")
        mkdir -p $(dirname $HIREPNAME)
        cp $FILE $HIREPNAME
    done 

}
# 5
clone_pycparser(){
    local PYCPARSER=$1
    git clone --depth=1 ${PYCPARSER_REMOTE} $PYCPARSER
}
# 6
analyse_callgraph(){
    local HIREP=$1
    local PYCPARSER=$2
    python3 $FFMODULE/main.py $FFMODULE/cpp_flags.yaml $HIREP $PYCPARSER
}
# 7 
copy_and_clean_selected_sources(){
    # TODO: maybe use a flat directory instead?    
    local HIREP=$1
    local SOMBRERO=$2
    for FILE in $(cat all_used_sources.txt)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        mkdir -p $(dirname $NEWFILE)
        python3 $FFMODULE/filter_source.py $FILE $NEWFILE all_unused_functions.txt
    done

}
# 8
copy_makefiles(){
    # Since we're not using a flat directory,
    # we need to also copy the makefiles
    # only those which do not exist!
    local HIREP=$1
    local SOMBRERO=$2
   
    for FILE in $(find $HIREP/LibHR -name Makefile)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        if [ -d $(dirname $NEWFILE) ]
        then
            if [ ! -f $NEWFILE ]
            then
                echo $(dirname $NEWFILE)
                cp $FILE $NEWFILE
            fi
        fi
    done
}
# 9
copy_selected_headers(){
    local FILELIST=$1
    local SOMBRERO=$2
    local UNUSED_FUNCTIONS=$3
    for FILE in $(cat $FILELIST)
    do
        echo $FILE
        NEWFILE=$SOMBRERO/Include/$(basename $FILE)
        python3 $FFMODULE/filter_header.py $FILE $NEWFILE $UNUSED_FUNCTIONS
    done 
}
#10 
copy_additional_files(){
    local FILELIST=$1
    local HIREP=$2
    local SOMBRERO=$3
    for FILE in $(cat $FILELIST)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        mkdir -p $(dirname $NEWFILE)
        cp $FILE $NEWFILE
    done
}
#11
clean_macros(){
   local SOMBRERO=$1
    $MACROMODULE/replace_macros.sh $SOMBRERO
}

#12
package(){
   local SOMBRERO=$1
   find $SOMBRERO -type f | grep -v '.git' | xargs tar -cvf sombrero.tar.gz
}
