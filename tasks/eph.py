"""
Ephemeral environment deployment tasks for the role-play application.

This module provides invoke tasks for managing ephemeral deployments
on Fly.io, including creation, deployment, and destruction of short-lived
testing applications.
"""

from invoke import Collection, task, Exit

APP_NAME = "role-play-ephemeral"
REGION = "cdg"  # Paris, France


@task
def create(context):
    """
    Create the ephemeral application on Fly.io.

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
def deploy(context, build=True, setup_token=True):
    """
    Deploy the application to ephemeral environment.

    Creates the Fly.io application if it doesn't exist, sets up Doppler token,
    and deploys the current version to the ephemeral environment.

    Args:
        context: The invoke context object for running commands.
        build: Whether to rebuild the Docker image (default: True).
        setup_token: Whether to setup Doppler token (default: True).
    """
    print(f"Deploying to ephemeral environment: {APP_NAME}")

    # Ensure app exists
    create(context)

    # Setup Doppler token as prerequisite for deployment
    if setup_token:
        print("🔑 Setting up Doppler token as prerequisite for deployment...")
        setup_doppler_token(context)
    else:
        print("⚠️  Skipping Doppler token setup (--no-setup-token flag used)")

    # Deploy the application using ephemeral config
    deploy_cmd = "flyctl deploy --config fly.ephemeral.toml"
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
    Check the status of the ephemeral application.

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
def logs(context):
    """
    View logs from the ephemeral application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Fetching logs from {APP_NAME}")
    try:
        context.run(f"flyctl logs --app {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        raise Exit(1)


@task
def ssh(context):
    """
    SSH into the ephemeral application.

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
    Scale the ephemeral application.

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
    List all secrets for the ephemeral application.

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
    Set a secret for the ephemeral application.

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
    Destroy the ephemeral application.

    Completely removes the ephemeral application from Fly.io.
    This action is irreversible but expected for ephemeral environments.

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

    print(f"Destroying ephemeral app: {APP_NAME}")
    try:
        context.run(f"flyctl apps destroy {APP_NAME} --yes")
        print(f"✅ Successfully destroyed {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to destroy app: {e}")
        raise Exit(1)


@task
def info(context):
    """
    Display information about the ephemeral application.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"App Information for {APP_NAME}")
    print(f"Region: {REGION}")
    print(f"URL: https://{APP_NAME}.fly.dev")
    print("⚠️  This is an ephemeral environment - expected to be short-lived")
    try:
        context.run(f"flyctl info --app {APP_NAME}")
    except Exception as e:
        print(f"❌ Failed to get app info: {e}")
        raise Exit(1)


@task
def quick_deploy(context):
    """
    Quick deploy without rebuild for faster ephemeral testing.

    Note: This still sets up Doppler token by default.
    Use deploy flags to skip this step for even faster deployments.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Quick deploying to {APP_NAME} (no rebuild, with token setup)")
    deploy(context, build=False, setup_token=True)


@task
def run(context):
    """
    Run the ephemeral application server.

    Starts the Django development server for the ephemeral environment.

    Args:
        context: The invoke context object for running commands.
    """
    print("Starting ephemeral application server...")
    context.run("python manage.py runserver 0.0.0.0:8000")


@task
def run_worker(context):
    """
    Run the Celery worker for ephemeral environment.

    Starts the Celery worker process to handle background tasks.

    Args:
        context: The invoke context object for running commands.
    """
    print("Starting ephemeral Celery worker...")
    context.run("celery -A role_play worker --loglevel=info")


@task
def deploy_release(context):
    """
    Run deployment release commands for ephemeral environment.

    Executes database migrations and other deployment setup tasks.

    Args:
        context: The invoke context object for running commands.
    """
    print("Running ephemeral deployment release commands...")
    context.run("doppler run -- python manage.py migrate")
    context.run("python manage.py collectstatic --noinput")


@task
def setup_doppler_token(context):
    """
    Generate a Doppler service token for dev config and set it in Fly secrets.

    Creates a service token named "fly-ephemeral" for the dev config and
    sets it as DOPPLER_TOKEN secret in the ephemeral Fly.io app.

    Args:
        context: The invoke context object for running commands.
    """
    print(f"Setting up Doppler token for {APP_NAME}")

    try:
        # Generate a service token for the dev config
        print("🔑 Generating Doppler service token for dev config...")
        result = context.run(
            "doppler configs tokens create fly-ephemeral --config dev --plain",
            hide=True,
        )

        # Extract the token from the output
        token = result.stdout.strip()

        if not token:
            print("❌ Failed to generate Doppler token - empty response")
            raise Exit(1)

        print("✅ Successfully generated Doppler service token")

        # Set the token as a secret in the Fly.io app
        print(f"🔄 Setting DOPPLER_TOKEN secret in {APP_NAME}...")
        context.run(
            f'flyctl secrets set DOPPLER_TOKEN="{token}" --app {APP_NAME}', hide=True
        )

        print(f"✅ Successfully set DOPPLER_TOKEN secret in {APP_NAME}")
        print("🎉 Doppler integration is now configured for the ephemeral environment")

    except Exception as e:
        print(f"❌ Failed to setup Doppler token: {e}")
        raise Exit(1)


namespace = Collection(
    create,
    deploy,
    destroy,
    status,
    logs,
    ssh,
    scale,
    secrets_list,
    secrets_set,
    info,
    quick_deploy,
    run,
    run_worker,
    deploy_release,
    setup_doppler_token,
)
