#!/bin/bash

SOURCE=${1-$USER/makers}
DESTINATION=${2-/var/www/makers}

echo Installing from $SOURCE to $DESTINATION

cp $SOURCE/makers/*.py $DESTINATION/makers
cp -r $SOURCE/scripts $DESTINATION
$SOURCE/scripts/setpassword

source /var/www/makers_venv/bin/activate
$DESTINATION/manage.py collectstatic
