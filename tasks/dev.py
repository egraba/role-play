from invoke import task


@task
def clean(c):
    """Clean generated files"""
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task(clean)
def build(c):
    """Load libraries and apply database migrations"""
    c.run("poetry install")
    c.run("python manage.py migrate")


@task(build)
def run(c):
    """Run the app"""
    c.run("python manage.py runserver")
