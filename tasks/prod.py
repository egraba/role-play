from invoke import task

from tasks import db


@task(db.migrate, db.load_settings)
def deploy(context):
    """Deploy the app"""
    pass


@task
def run(context):
    """Run the app"""
    context.run("python manage.py collectstatic")
    context.run("daphne role_play.asgi:application -b 0.0.0.0 -p $PORT --access-log -")


@task
def run_worker(context):
    """Run Celery worker"""
    context.run("celery -A role_play worker -l INFO", asynchronous=True)
