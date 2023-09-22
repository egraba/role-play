from invoke import task


@task
def clean(c):
    patterns = ["htmlcov", "staticfiles", ".coverage"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task
def run(c):
    c.run("python manage.py runserver")
