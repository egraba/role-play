from invoke import Collection

import tasks.db as db
import tasks.dev as dev
import tasks.prod as prod
import tasks.test as test

namespace = Collection(dev, db, test, prod)
