#!/bin/bash

mkdir dbs
while True; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
		break
	fi
	echo "Upragde command failed, retrying in 5 seconds..."
	sleep 5
done

exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:app
