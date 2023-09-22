from invoke import task


@task(
    help={
        "coverage": "Measure test coverage",
        "verbose": "Increase verbosity",
        "test_label": "Module paths to test (i.e Django test_label option)",
    }
)
def run(c, coverage=False, verbose=False, test_label=None):
    """Test the app"""
    cmd_options = ""
    if verbose:
        cmd_options += "--verbosity=2"
    if test_label:
        cmd_options += test_label
    if coverage:
        c.run(f"coverage run manage.py test {cmd_options}")
        c.run("coverage html")
    else:
        c.run(f"python manage.py test {cmd_options}")
