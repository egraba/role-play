from invoke import task


@task
def reset(c):
    """Reset the DB"""
    c.run("python manage.py reset_db")


@task
def load_settings(c):
    """Load app settings"""
    c.run("python manage.py loaddata abilities")
    c.run("python manage.py loaddata advancement")
    c.run("python manage.py loaddata races")
    c.run("python manage.py loaddata classes")


@task(load_settings)
def populate(c):
    """Populate the DB with realistic data"""
    c.run("python manage.py populatedb")
