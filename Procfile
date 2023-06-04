web: pipenv sync && pipenv run python manage.py migrate && pipenv run python manage.py collectstatic && pipenv run gunicorn role_play.wsgi --capture-output --access-logfile - --log-file -
