from invoke import Collection

from tasks import db, dev, prod, stg, test

namespace = Collection(dev, db, test, stg, prod)
