#!/bin/sh

if [ "$DATABASE" = "postgresql" ]
then
    echo "Waiting for postgresql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata data/initial_data.json
python manage.py collectstatic --no-input
python manage.py createsuperuser --username superuser --email superuser@example.com --no-input
python manage.py generate-random-data
npm run dev &

exec "$@"