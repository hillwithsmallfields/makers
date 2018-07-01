#!/bin/bash

SOURCE=${1-$USER/makers}
DESTINATION=${2-/var/www/makers}

echo Installing from $SOURCE to $DESTINATION

echo copying python files
cp $SOURCE/makers/*.py $DESTINATION/makers
echo copying scripts
cp $SOURCE/scripts/* $DESTINATION/scripts
echo Copying apps
for APP in $SOURCE/apps
do
    cp -r $APP $DESTINATION
done
echo poking password
$SOURCE/scripts/setpassword
echo activating venv
source /var/www/makers_venv/bin/activate
echo setting up static files
$DESTINATION/manage.py collectstatic
