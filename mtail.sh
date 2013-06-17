#!/bin/bash

# This script returns all lines from a log file that appeared after the previous run with similar service name
# or simply the entire log file on first run or after log rotation


# $1 - path to log, $2 - service name
if [ $# -ne 2 ] ; then
	echo "usage: ${0} [path to log] [service name], not $0 $@"
	exit 1
fi
 
# Path to temporary files
TMPDIR=/tmp/mtail
if [ ! -d $TMPDIR ] ; then
	mkdir -p $TMPDIR
fi

TMP_HASH=`echo -n "$1" | md5sum | awk '{print \$1}'`
TMP_FILE="${TMPDIR}/${TMP_HASH}_${2}"

if [ ! -f "${1}" ] ; then
	echo "Log file ${1} does not exist"
	exit 1
fi

# Get size of log file in bytes
LENGTH=`du -bs ${1} | awk '{print \$1}'`

# Get number of bytes that have been already displayed
if [ ! -e $TMP_FILE ] ; then
	OFFSET=0
else
	OFFSET=`cat $TMP_FILE`
fi

# Check if log is rotated, and therefore its length is less than the last offset
if [ $OFFSET -gt $LENGTH ] ; then
	OFFSET=0
fi

echo -n $LENGTH > $TMP_FILE

tail -c "+${OFFSET}" $1


