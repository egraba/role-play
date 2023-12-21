from invoke import task


@task
def clean(context):
    """Clean generated files"""
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        context.run(f"rm -rf {pattern}")


@task(clean)
def build(context):
    """Apply database migrations"""
    context.run("python manage.py migrate", pty=True)


@task(build)
def run(context):
    """Run the app"""
    context.run("python manage.py runserver", pty=True)


@task
def run_worker(context):
    """Run Celery worker"""
    context.run("celery -A role_play worker -l INFO", pty=True)


@task
def shell(context):
    """Launch Django shell"""
    context.run("python manage.py shell")
