# -*- coding: utf-8 -*-


from oleander import app, db
import fixtures
import sys


class AppMixin(object):

    def setUp(self):
        app.config.from_pyfile('../settings/testing.py')
        assert app.config['TESTING'] == True
        self.app = app



class DatabaseMixin(AppMixin):

    def setUp(self):
        super(DatabaseMixin, self).setUp()
        db.init_app(self.app)

        db.drop_all()
        db.create_all()

        fixtures.install(db.session, *fixtures.all_data)
        db.session.flush()

    def tearDown(self):
        db.session.remove()
        super(DatabaseMixin, self).tearDown()

