#!flask/bin/python
import imp
from migrate.versioning import api
from app import db
from config import Config
#from config import SQLALCHEMY_DATABASE_URI
#from config import SQLALCHEMY_MIGRATE_REPO
migration = Config.SQLALCHEMY_MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(Config.SQLALCHEMY_DATABASE_URI, Config.SQLALCHEMY_MIGRATE_REPO) + 1)
tmp_module = imp.new_module('old_model')
old_model = api.create_model(Config.SQLALCHEMY_DATABASE_URI, Config.SQLALCHEMY_MIGRATE_REPO)
#print (old_model)
#print(tmp_module.__dict__)
#exec (old_model in tmp_module.__dict__)
exec (old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(Config.SQLALCHEMY_DATABASE_URI, Config.SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(Config.SQLALCHEMY_DATABASE_URI, Config.SQLALCHEMY_MIGRATE_REPO)
print ('New migration saved as ' + migration)
print ('Current database version: ' + str(api.db_version(Config.SQLALCHEMY_DATABASE_URI, Config.SQLALCHEMY_MIGRATE_REPO)))
