"""
Staging environment deployment tasks for the role-play application.

This module provides invoke tasks for managing the staging deployment
on Fly.io, including creation, deployment, and destruction of the
staging application.
"""

from invoke import Collection, task, Exit

APP_NAME = "role-play-staging"
REGION = "fra"  # Frankfurt region


@task
def create(context):
    """
    Create the staging application on Fly.io.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Creating Fly.io app: {APP_NAME}")
    try:
        context.run(f"flyctl apps create {APP_NAME}")
        print(f"✅ Successfully created {APP_NAME}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"⚠️  App {APP_NAME} already exists, skipping creation")
        else:
            print(f"❌ Failed to create app: {e}")
            raise Exit(1)


@task
def deploy(context, build=True):
    """
    Deploy the application to staging environment.

    Creates the Fly.io application if it doesn't exist and deploys
    the current version to the staging environment.

    Args:
        context: The invoke context object for running commands.
        build: Whether to rebuild the Docker image (default: True).
    """
    print(f"Deploying to staging environment: {APP_NAME}")

    # Ensure app exists
    create(context)

    # Deploy the application
    deploy_cmd = f"flyctl deploy --app {APP_NAME}"
    if not build:
        deploy_cmd += " --no-build"

    try:
        context.run(deploy_cmd)
        print(f"✅ Successfully deployed to {APP_NAME}")
        print(f"🌐 App URL: https://{APP_NAME}.fly.dev")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise Exit(1)


@task
def status(context):
    """
    Check the status of the staging application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Checking status of {APP_NAME}")
    try:
        context.run(f"flyctl status --app {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to get status: {e}")
        raise Exit(1)


@task
def logs(context, lines=50):
    """
    View logs from the staging application.

    Args:
        context: The invoke context object for running commands.
        lines: Number of log lines to display (default: 50).
    """
    print(f"Fetching {lines} lines of logs from {APP_NAME}")
    try:
        context.run(f"flyctl logs --app {APP_NAME} --lines {lines}")
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        raise Exit(1)


@task
def ssh(context):
    """
    SSH into the staging application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Connecting to {APP_NAME} via SSH")
    try:
        context.run(f"flyctl ssh console --app {APP_NAME}")
    except Exception as e:
        print(f"❌ SSH connection failed: {e}")
        raise Exit(1)


@task
def scale(context, count=1):
    """
    Scale the staging application.

    Args:
        context: The invoke context object for running commands.
        count: Number of instances to scale to (default: 1).
    """
    print(f"Scaling {APP_NAME} to {count} instances")
    try:
        context.run(f"flyctl scale count {count} --app {APP_NAME}")
        print(f"✅ Successfully scaled to {count} instances")
    except Exception as e:
        print(f"❌ Scaling failed: {e}")
        raise Exit(1)


@task
def secrets_list(context):
    """
    List all secrets for the staging application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Listing secrets for {APP_NAME}")
    try:
        context.run(f"flyctl secrets list --app {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to list secrets: {e}")
        raise Exit(1)


@task
def secrets_set(context, key, value):
    """
    Set a secret for the staging application.

    Args:
        context: The invoke context object for running commands.
        key: The secret key name.
        value: The secret value.
    """
    print(f"Setting secret {key} for {APP_NAME}")
    try:
        context.run(f"flyctl secrets set {key}={value} --app {APP_NAME}")
        print(f"✅ Successfully set secret {key}")
    except Exception as e:
        print(f"❌ Failed to set secret: {e}")
        raise Exit(1)


@task
def destroy(context, confirm=False):
    """
    Destroy the staging application.

    Completely removes the staging application from Fly.io.
    This action is irreversible.

    Args:
        context: The invoke context object for running commands.
        confirm: Skip confirmation prompt if True.
    """
    if not confirm:
        response = input(
            f"Are you sure you want to destroy {APP_NAME}? This cannot be undone. (y/N): "
        )
        if response.lower() != "y":
            print("❌ Destruction cancelled")
            return

    print(f"Destroying {APP_NAME}")
    try:
        context.run(f"flyctl apps destroy {APP_NAME} --yes")
        print(f"✅ Successfully destroyed {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to destroy app: {e}")
        raise Exit(1)


@task
def info(context):
    """
    Display information about the staging application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"App Information for {APP_NAME}")
    print(f"Region: {REGION}")
    print(f"URL: https://{APP_NAME}.fly.dev")
    try:
        context.run(f"flyctl info --app {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to get app info: {e}")
        raise Exit(1)


namespace = Collection(
    create, deploy, destroy, status, logs, ssh, scale, secrets_list, secrets_set, info
)
