#!/bin/bash

# Run this script as root; I've tried the commands that make it up, under Raspbian 9.3 on a Raspberry Pi 3B+

apt-get install nginx
apt-get install virtualenv
cd /var/www
virtualenv --python=python3 --always-copy makers_venv
source makers_venv/bin/activate
pip install django
pip install gunicorn
