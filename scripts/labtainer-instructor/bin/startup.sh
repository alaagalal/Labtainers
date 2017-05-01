#!/usr/bin/env bash

# startup.sh
# Arguments: None
#
# Usage: startup.sh
# 
# Description: Concatenate instructions.txt file and pipe to less

LOCKDIR=/tmp/.mylockdir
if mkdir "$LOCKDIR" >/dev/null 2>&1; then
    echo "Starting startup.sh"
    cat "$HOME"/instructions.txt | less
fi