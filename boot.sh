#!/bin/bash

mkdir dbs
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:app