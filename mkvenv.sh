#!/bin/sh

if [ -n "$BASH_SOURCE" ]; then
    THIS_SCRIPT=$BASH_SOURCE
elif [ -n "$ZSH_NAME" ]; then
    THIS_SCRIPT=$0
else
    THIS_SCRIPT="$(pwd)/mkvenv.sh"
fi


scriptdir=$(cd $(dirname $THIS_SCRIPT); pwd)
venv=$scriptdir/venv
unset THIS_SCRIPT

create_venv() {
    local venv=$1
    if [ -z "$VIRTUALENV" ]; then
        local possible
        for possible in virtualenv-3 virtualenv
        do
            local try=$(which $possible)
            if [ -e $try ]; then
                local VIRTUALENV=$try
                break
            fi
        done
    fi

    if [ -z "$VIRTUALENV" ]; then
        echo "Could not find virtualenv on the path"
    else
        $VIRTUALENV $venv
    fi
}

if [ ! -d $venv ]; then
    create_venv $venv
fi

if [ -d $venv ]; then
    . $venv/bin/activate
else
    echo "No virtual environment available to activate"
fi
