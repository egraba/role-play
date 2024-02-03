from invoke import Collection

from tasks import db, dev, prod, test

namespace = Collection(dev, db, test, prod)
