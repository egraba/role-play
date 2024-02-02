from invoke import task

import tasks.db as db


@task
def run_worker(context):
    """Run Celery worker"""
    context.run("celery -A role_play worker -l INFO", asynchronous=True)


@task(run_worker)
def build(context):
    """Apply database migrations"""
    context.run("poetry run python manage.py migrate")


@task(build, db.load_settings)
def deploy(context):
    """Deploy the app"""
    context.run("poetry run python manage.py collectstatic")
    context.run(
        "poetry run daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log -"
    )
