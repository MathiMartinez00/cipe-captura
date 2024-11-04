#!/bin/sh

if [ "$DATABASE" = "postgresql" ]
then
    echo "Waiting for postgresql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py sync-data-with-captura

exec "$@"