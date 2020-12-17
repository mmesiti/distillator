#!/usr/bin/env bash
set -euo pipefail

ROOTDIR=$1
INCLUDE=$ROOTDIR/Include
# From https://stackoverflow.com/a/246128/3113564
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

TMPDIR=${SCRIPT_LOCATION}/TMP
mkdir -p $TMPDIR
python ${SCRIPT_LOCATION}/main.py $ROOTDIR $TMPDIR

INCLUDE_BACKUP=${SCRIPT_LOCATION}/include_backup

mkdir -p ${INCLUDE_BACKUP}

for file in $TMPDIR/used_macros_by_grouprep/*.h $TMPDIR/used_macros_by_grouprep_repr_func/*.h
do
    BASENAME=$(basename $file)
    echo "Saving original version of $BASENAME..." 
    cp $INCLUDE/$BASENAME $INCLUDE_BACKUP 
    echo "Replacing $BASENAME..." 
    cp $file $INCLUDE
done

