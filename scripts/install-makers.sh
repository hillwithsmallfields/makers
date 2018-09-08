#!/bin/bash

# Enough overrides to let you install a testing version too, I hope:
MAINCONF=${1-makers.yaml}
SOURCE=${2-$USER/open-projects/makers}
DESTINATION=${3-/var/www/makers}
CONFDEST=${4-/usr/local/share/makers}

echo Installing with config $MAINCONF from $SOURCE to $DESTINATION and $CONFDEST

echo Copying config files
mkdir -p $CONFDEST
cp -r $SOURCE/help_texts $CONFDEST
chmod a+rx $CONFDEST
cd $SOURCE/config/
cp $MAINCONF *.css makers.js $CONFDEST
cp -r message_templates $CONFDEST
chmod -R a+r $CONFDEST/*

mkdir -p $DESTINATION

echo copying python files
cp $SOURCE/manage.py $SOURCE/makers/*.py $DESTINATION/makers

echo copying scripts
cp $SOURCE/scripts/* $DESTINATION/scripts

echo Copying apps from $SOURCE/apps
for APP in $SOURCE/apps/*
do
    echo Copying $APP to $DESTINATION
    cp -r $APP $DESTINATION
done

echo Copying common code
for PART in model pages untemplate
do
    mkdir -p $DESTINATION/$PART
    cp $SOURCE/$PART/*.py $DESTINATION/$PART
done

echo Copying static files
mkdir -p $DESTINATION/static
for APPDIR in $SOURCE/makers $SOURCE/apps/*
do
    cp -r $APPDIR/static/* $DESTINATION/static
done

echo poking password
$SOURCE/scripts/setpassword

echo activating venv
source /var/www/makers_venv/bin/activate

echo setting up static files
$DESTINATION/manage.py collectstatic --no-input --no-color

echo makers installation complete
