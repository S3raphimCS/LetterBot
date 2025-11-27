#!/bin/sh

python "manage.py" migrate --noinput

python "manage.py" collectstatic --noinput

#python "manage.py" start_webhook

gunicorn -c "$PROJECT_ROOT/gunicorn.conf.py" server.wsgi:application