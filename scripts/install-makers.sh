#!/bin/bash

SOURCE=${$1-$(pwd)}
DESTINATION=${2-/var/www/makers}

cp $SOURCE/makers/*.py $DESTINATION/makers
