from invoke import task


@task
def flush(c):
    """Flush the DB"""
    c.run("python manage.py flush")


@task()
def populate(c):
    """Populate the DB with realistic data"""
    c.run("python manage.py loaddata abilities")
    c.run("python manage.py loaddata advancement")
    c.run("python manage.py loaddata races")
    c.run("python manage.py loaddata classes")
    c.run("python manage.py populatedb")
