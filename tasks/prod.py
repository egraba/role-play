from invoke import task

import tasks.db as db


@task
def run_worker(c):
    """Run Celery worker"""
    c.run("celery -A role_play worker -l INFO", asynchronous=True)


@task(run_worker)
def build(c):
    """Apply database migrations"""
    c.run("poetry run python manage.py migrate")


@task(build, db.load_settings)
def deploy(c):
    """Deploy the app"""
    c.run("poetry run python manage.py collectstatic")
    c.run(
        "poetry run daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log -"
    )
