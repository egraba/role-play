from invoke import task


@task
def clean(c):
    """Clean generated files"""
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task
def make_migrations(c):
    """Make Django migrations"""
    c.run("python manage.py makemigrations", pty=True)


@task(clean)
def build(c):
    """Apply database migrations"""
    c.run("python manage.py migrate", pty=True)


@task(build)
def run(c):
    """Run the app"""
    c.run("python manage.py runserver", pty=True)


@task
def run_worker(c):
    """Run Celery worker"""
    c.run("celery -A role_play worker -l INFO", pty=True)


@task
def shell(c):
    """Launch Django shell"""
    c.run("python manage.py shell")
