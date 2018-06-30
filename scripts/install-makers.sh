#!/bin/bash

SOURCE=${$1-$(pwd)}
DESTINATION=${2-/var/www/makers}

echo Installing from $SOURCE to $DESTINATION

echo cp $SOURCE/makers/*.py $DESTINATION/makers
cp $SOURCE/makers/*.py $DESTINATION/makers
