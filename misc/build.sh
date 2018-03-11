#!/bin/bash

TARGET=$HOME/makers-bin

if [ -d $TARGET ]
then
    rm $TARGET/*
else
    mkdir $TARGET
fi

cp common/*.py pages/*.py utils/*.py $TARGET
cp config/*.yaml $TARGET
