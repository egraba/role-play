from invoke import task


@task(help={"coverage": "Measure test coverage", "verbose": "Increase verbosity"})
def run(c, coverage=False, verbose=False):
    """Test the app"""
    cmd_options = ""
    if verbose:
        cmd_options += "--verbosity=2"
    if coverage:
        c.run(f"coverage run manage.py test {cmd_options}")
        c.run("coverage html")
    else:
        c.run(f"python manage.py test {cmd_options}")
