from invoke import task


@task(help={"coverage": "Measure test coverage"})
def run(c, coverage=False):
    """Test the app"""
    if coverage:
        c.run("coverage run manage.py test")
        c.run("coverage html")
    else:
        c.run("python manage.py test")
