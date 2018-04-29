#!/bin/bash

mv local.db local.db_`date +%Y%m%d%H%M%S`
./manage.py migrate
./manage.py loadtestdata
