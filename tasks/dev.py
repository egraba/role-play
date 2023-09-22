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
    c.run("python manage.py makemigrations")


@task(clean)
def build(c):
    """Apply database migrations"""
    c.run("python manage.py migrate")


@task(build)
def run(c):
    """Run the app"""
    c.run("python manage.py runserver")
