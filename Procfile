web: poetry sync && poetry run python manage.py migrate && poetry run python manage.py collectstatic && poetry run daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log -
