# -*- coding: utf-8 -*-


from flask.ext.script import Server, Manager, Shell
from app import app
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


if __name__ == "__main__":
    manager.run()
