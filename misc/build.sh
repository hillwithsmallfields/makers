#!/bin/bash

TARGET=$HOME/makers-bin
DATA=$HOME/makers-data

for DIR in $TARGET $DATA
do
    if [ -d $DIR ]
    then
        echo rm $DIR/*
    else
        mkdir $DIR
    fi
done

cp common/*.py pages/*.py utils/*.py $TARGET
cp config/*.yaml $DATA
cp misc/testing-data.json $DATA/data.json
