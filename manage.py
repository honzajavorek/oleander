# -*- coding: utf-8 -*-


from flask.ext.script import Server, Manager, Shell
from oleander import app, db
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
    return nose.run() # argv=[test_module]


@manager.command
def resetdb():
    """Drops all tables and recreates them from scratch."""
    if not app.debug:
        # to prevent accidental disasters
        raise RuntimeError('Application is not in debug mode.')
    db.drop_all()
    db.create_all()


if __name__ == "__main__":
    manager.run()
