from invoke import task


@task
def reset(c):
    """Reset the DB"""
    c.run("python manage.py reset_db", pty=True)


@task
def load_settings(c):
    """Load app settings"""
    patterns = ["abilities", "advancement", "races", "classes", "equipment"]
    for pattern in patterns:
        c.run(f"python manage.py loaddata {pattern}", pty=True)


@task(load_settings)
def populate(c):
    """Populate the DB with realistic data"""
    c.run("python manage.py populatedb", pty=True)


@task
def make_migrations(c):
    """Make Django migrations"""
    c.run("python manage.py makemigrations", pty=True)
