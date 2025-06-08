from invoke import Collection

from tasks import db, dev, prod, stg, test, eph

namespace = Collection(dev, db, test, eph, stg, prod)
