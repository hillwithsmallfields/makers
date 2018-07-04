#!/bin/bash

SOURCE=${1-$USER/makers}
DESTINATION=${2-/var/www/makers}

echo Installing from $SOURCE to $DESTINATION

echo Copying config files
sudo bash <<EOF
mkdir -p /usr/local/share/makers
chmod a+rx /usr/local/share/makers
cp $SOURCE/config/makers.yaml /usr/local/share/makers/makers.yaml
cp $SOURCE/config/makers.css /usr/local/share/makers/makers.css
chmod a+r /usr/local/share/makers/*
EOF

echo copying python files
cp $SOURCE/makers/*.py $DESTINATION/makers
echo copying scripts
cp $SOURCE/scripts/* $DESTINATION/scripts
echo Copying apps from $SOURCE/apps
for APP in $SOURCE/apps/*
do
    echo Copying $APP to $DESTINATION
    cp -r $APP $DESTINATION
done
echo poking password
$SOURCE/scripts/setpassword
echo activating venv
source /var/www/makers_venv/bin/activate
echo setting up static files
$DESTINATION/manage.py collectstatic --no-input --no-color
