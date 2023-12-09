from invoke import task


@task(
    help={
        "coverage": "Measure test coverage",
        "verbose": "Increase verbosity",
        "test_label": "Module paths to test",
    }
)
def run(c, coverage=False, verbose=False, test_label=None, pty=True):
    """Test the app"""
    cmd = "pytest --color=yes"
    cmd_options = ""
    if verbose:
        cmd_options += "--verbose"
    if test_label:
        cmd_options += test_label
    if coverage:
        c.run(f"coverage run -m {cmd} {cmd_options}")
        c.run("coverage html")
    else:
        c.run(f"{cmd} {cmd_options}")
