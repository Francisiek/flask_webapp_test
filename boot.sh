#!/bin/bash

mkdir dbs
flask db upgrade
SECRET_KEY=$(python3 -c "from random import randint; print(hex(randint(2**64, 10**72)))")

exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:app