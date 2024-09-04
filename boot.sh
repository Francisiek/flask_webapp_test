#!/bin/bash

while true; do
  echo "Running flask db upgrade..."
	flask db upgrade
	if [[ "$?" == "0" ]]; then
		break
	fi
	echo "Upragde command failed, retrying in 5 seconds..."
	sleep 5
done
echo "Running gunicorn server"
exec gunicorn -b :5000 --access-logfile - --error-logfile - blog:app
