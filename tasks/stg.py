"""
Staging environment deployment tasks for the role-play application.

This module provides invoke tasks for managing the staging deployment
on Fly.io, including creation, deployment, and destruction of the
staging application.
"""

from invoke import Collection, task

APP_NAME = "role-play-staging"


@task
def deploy(context):
    """
    Deploy the application to staging environment.

    Creates the Fly.io application if it doesn't exist and deploys
    the current version to the staging environment.

    Args:
        context: The invoke context object for running commands.
    """
    context.run(f"flyctl apps create {APP_NAME}")
    context.run(f"flyctl deploy --app {APP_NAME}")


@task
def destroy(context):
    """
    Destroy the staging application.

    Completely removes the staging application from Fly.io.
    This action is irreversible.

    Args:
        context: The invoke context object for running commands.
    """
    context.run(f"flyctl apps destroy {APP_NAME} --yes")


namespace = Collection(deploy, destroy)
