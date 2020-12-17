#!/usr/bin/env bash
set -euo pipefail

HIREP=HiRep
SOMBRERO=sombrero
PYCPARSER=pycparser

# From https://stackoverflow.com/a/246128/3113564
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

FFMODULE=$SCRIPT_LOCATION/files_and_functions
MACROMODULE=$SCRIPT_LOCATION/macros

export PYTHONPATH=$FFMODULE:$MACROMODULE

# 1
clone_hirep(){
    HIREP_REMOTE=git@github.com:sa2c/HiRep
    git clone --depth=1 ${HIREP_REMOTE} ${HIREP} 
}
clone_hirep
# 2
generate_headers(){
    echo "Preparing MkFlags"
    MKFLAGS=${HIREP}/Make/MkFlags
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
generate_headers
# 3
clone_sombrero(){
    #SOMBRERO_REMOTE=git@github.com:mmesiti/sombrero
    SOMBRERO_REMOTE=/home/michele/hirep-workspace/gantry_sombrero/sombrero
    git clone --depth=1 ${SOMBRERO_REMOTE} --branch test $SOMBRERO  

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
clone_sombrero
# 4
clone_pycparser(){
    PYCPARSER_REMOTE=git@github.com:eliben/pycparser.git
    git clone --depth=1 ${PYCPARSER_REMOTE} $PYCPARSER
}
clone_pycparser
# 5
analyse_callgraph(){
python3 $FFMODULE/main.py $FFMODULE/cpp_flags.yaml $HIREP $PYCPARSER
}

analyse_callgraph

#  6 
copy_selected_sources(){
    # TODO: maybe use a flat directory instead?    
    for FILE in $(cat all_used_sources.txt)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        mkdir -p $(dirname $NEWFILE)
        python3 $FFMODULE/filter_file.py $FILE $NEWFILE all_unused_functions.txt
    done

}
copy_selected_sources 
# 7
copy_makefiles(){
    # Since we're not using a flat directory,
    # we need to also copy the makefiles
    # only those which do not exist!
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
copy_makefiles

# 6
copy_selected_headers(){
    for FILE in $(cat used_headers.txt)
    do
        cp $FILE $SOMBRERO/Include 
    done 
}
copy_selected_headers 

# 7
copy_additional_files(){
    for FILE in $(cat $SCRIPT_LOCATION/additional_files_to_copy.txt)
    do
        NEWFILE=$(sed 's|'$HIREP'|'$SOMBRERO'|' <<< "$FILE")
        mkdir -p $(dirname $NEWFILE)
        cp $FILE $NEWFILE
    done
}

copy_additional_files 

# 8
clean_macros(){
    $MACROMODULE/replace_macros.sh $SOMBRERO
}
clean_macros

#######
cd sombrero
for i in {1..6}
do
    make sombrero/sombrero$i && mpirun -n 16 --oversubscribe ./sombrero/sombrero$i -l 8x8x8x8 -p 2x2x2x2
done 
