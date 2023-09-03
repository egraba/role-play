web: poetry install --without=dev \
  && poetry run python manage.py migrate \
  && poetry run python manage.py collectstatic \
  && poetry run python manage.py loaddata advancement
  && poetry run daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log - \
