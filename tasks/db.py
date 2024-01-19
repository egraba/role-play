from invoke import task


@task
def reset(context):
    """Reset the DB"""
    context.run("python manage.py reset_db", pty=True)


@task
def load_settings(context):
    """Load app settings"""
    patterns = [
        "senses",
        "advancement",
        "abilities",
        "races",
        "classes",
        "skills",
        "equipment",
    ]
    for pattern in patterns:
        context.run(f"python manage.py loaddata {pattern}", pty=True)


@task(load_settings)
def populate(context):
    """Populate the DB with realistic data"""
    context.run("python manage.py populatedb", pty=True)


@task
def make_migrations(context):
    """Make Django migrations"""
    context.run("python manage.py makemigrations", pty=True)
