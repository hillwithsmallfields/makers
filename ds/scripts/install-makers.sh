#!/bin/bash -x

# Enough overrides to let you install a testing version too, I hope:
MAINCONF=${1-makers.yaml}
SOURCE=${2-$HOME/open-projects/makers}
DESTINATION=${3-/var/www/makers}
CONFDEST=${4-/usr/local/share/makers}

rm -rf $DESTINATION

echo Installing with config $MAINCONF from $SOURCE to $DESTINATION and $CONFDEST

echo Copying config files
mkdir -p $CONFDEST
cp -r $SOURCE/help_texts $CONFDEST
chmod a+rx $CONFDEST
cd $SOURCE/config/
cp $MAINCONF *.css makers.js $CONFDEST
cp -r message_templates $CONFDEST
chmod -R a+r $CONFDEST/*

mkdir -p $DESTINATION ${DESTINATION}-files

echo copying python files
cp $SOURCE/manage.py $DESTINATION
mkdir -p $DESTINATION/makers
cp $SOURCE/makers/*.py $DESTINATION/makers

echo copying scripts
mkdir -p $DESTINATION/scripts
cp $SOURCE/scripts/* $DESTINATION/scripts

echo Copying apps from $SOURCE/apps
for APP in $SOURCE/apps/*
do
    echo Copying $APP to $DESTINATION
    cp -r $APP $DESTINATION
done

echo Copying common code
for PART in model pages untemplate makers
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

echo Copying static pages
mkdir -p $DESTINATION/files
cp -r $SOURCE/files/* $DESTINATION/files

echo activating venv
source /var/www/makers_venv/bin/activate

source /host/settings.sh
secret_key=$(tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c50)
cat <<EOF > /var/www/makers/.env
DJANGO_SECRET_KEY='$secret_key'
POSTGRES_PASSWORD='$POSTGRESNEWPW'

SMTP_HOST=$SMTP_HOST
SMTP_PORT=$SMTP_PORT
SMTP_USERNAME=$SMTP_USERNAME
SMTP_PASSWORD=$SMTP_PASSWORD
DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME
EOF

echo setting up static files
$DESTINATION/manage.py collectstatic --no-input --no-color

echo makers installation complete
