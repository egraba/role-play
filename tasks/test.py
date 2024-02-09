from invoke import task


@task(
    help={
        "coverage": "Measure test coverage",
        "verbose": "Increase verbosity",
        "test_label": "Module paths to test",
    }
)
def run(context, coverage=False, verbose=False, test_label=None):
    """Test the app"""
    cmd = "pytest --color=yes"
    cmd_options = ""
    if verbose:
        cmd_options += "--verbose"
    if test_label:
        cmd_options += test_label
    if coverage:
        context.run(f"coverage run -m {cmd} {cmd_options}", pty=True)
        context.run("coverage xml", pty=True)
        context.run("coverage html", pty=True)
    else:
        context.run(f"{cmd} {cmd_options}", pty=True)
