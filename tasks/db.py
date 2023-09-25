from invoke import task


@task
def reset(c):
    """Reset the DB"""
    c.run("python manage.py reset_db")


@task
def load_settings(c):
    """Load app settings"""
    patterns = ["abilities", "advancement", "races", "classes"]
    for pattern in patterns:
        c.run(f"python manage.py loaddata {pattern}")


@task(load_settings)
def populate(c):
    """Populate the DB with realistic data"""
    c.run("python manage.py populatedb")
