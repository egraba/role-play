from invoke import Collection

import tasks.db as db
import tasks.dev as dev
import tasks.test as test

namespace = Collection(dev, db, test)
