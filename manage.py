# -*- coding: utf-8 -*-


from flask.ext.script import Server, Manager, Shell
from oleander import app, db
import fixtures
import nose


# manager
manager = Manager(app)


# custom commands
manager.add_command('runserver', Server())


@manager.command
def runtests():
    """Runs unit tests."""
    # http://packages.python.org/Flask-Script/
    # http://readthedocs.org/docs/nose/en/latest/usage.html
    return nose.run(argv=['oleander.tests']) # argv=[test_module]


@manager.command
def createdb():
    """Creates all tables from scratch."""
    db.create_all()


@manager.command
def resetdb():
    """Drops all tables and recreates them from scratch including fixtures."""
    if not (app.debug or app.config['TESTING']):
        print "Application is not in debug mode!"
    else:
        db.drop_all()
        db.create_all()
        fixtures.install(db.session, *fixtures.all_data)
        db.session.commit()


if __name__ == "__main__":
    manager.run()
