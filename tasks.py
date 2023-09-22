from invoke import task


@task
def clean(c):
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task(clean)
def build(c):
    c.run("poetry install")
    c.run("python manage.py migrate")


@task(build)
def run(c):
    c.run("python manage.py runserver")
