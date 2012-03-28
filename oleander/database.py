# -*- coding: utf-8 -*-


class Transaction(object):
    """Context manager handling transactions in a readable way."""

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self.db.session

    def __exit__(self, type, value, traceback):
        if not value:
            self.db.session.commit()

