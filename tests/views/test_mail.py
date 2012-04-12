# -*- coding: utf-8 -*-


import unittest
from oleander import app, db


class TestSendGrid(unittest.TestCase):

    # app.config.from_pyfile($PROJECT_DIR/settings/testing.py)

    # def setUp(self):
    #     self.db_file_desc, app.config['DATABASE'] = tempfile.mkstemp()
    #     app.config['TESTING'] = True
    #     self.app = app.test_client()
    #     db.create_all()
    #     fixtures.install(db.session, *fixtures.all_data)

    def test_blabla(self):
        pass

    def test_bla(self):
        pass

    # def tearDown(self):
    #     os.close(self.db_fd)
    #     os.unlink(flaskr.app.config['DATABASE'])
