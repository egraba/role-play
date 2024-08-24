from invoke import Collection, task

from .db import migrate


@task
def clean(context):
    """Clean generated files"""
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        context.run(f"rm -rf {pattern}")


@task(migrate)
def run(context):
    """Run the app"""
    context.run("python manage.py runserver", pty=True)


@task
def run_worker(context):
    """Run Celery worker"""
    context.run(
        "celery -A role_play worker --beat --scheduler django --loglevel=info", pty=True
    )


@task
def shell(context):
    """Launch Django shell"""
    context.run("python manage.py shell")


namespace = Collection(clean, run, run_worker, shell)
