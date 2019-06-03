#!/bin/bash -x

# Run this script as root; I've tried the commands that make it up, under Raspbian 9.3 on a Raspberry Pi 3B+
# It needs the environment variable POSTGRESNEWPW set (so that it doesn't have to be written into the script)

# Postgresql setup commands based on https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04

source /host/settings.sh

apt-get install nginx virtualenv postgresql postgresql-server-dev-all mongodb
sudo -u postgres psql <<EOF
CREATE DATABASE makers;
CREATE USER makersuser WITH PASSWORD '$POSTGRESNEWPW';
ALTER ROLE makersuser SET client_encoding TO 'utf8';
ALTER ROLE makersuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE makersuser SET timezone to 'UTC';
GRANT ALL PRIVILEGES ON DATABASE makers to makersuser;
\q
EOF
apt-get install postgresql-server-dev-all
cd /var/www
virtualenv --python=python3 --always-copy makers_venv
source makers_venv/bin/activate
pip install django
pip install gunicorn
pip install pytz
pip install pyyaml
pip install yattag
pip install python-decouple
pip install bson
pip install pymongo
pip install python-resize-image

pip install boto3
pip install django-storages

pip install psycopg2

echo Using sudo to create log directory
mkdir -p /var/log/gunicorn
chown www-data:www-data /var/log/gunicorn

# later
# ./manage.py makemigrations
# ./manage.py migrate
# ./manage.py createsuperuser
