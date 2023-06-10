web: pipenv sync && pipenv run python manage.py migrate && pipenv run python manage.py collectstatic && pipenv run daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log -
