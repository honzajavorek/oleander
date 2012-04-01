# -*- coding: utf-8 -*-


from fixture import DataSet, SQLAlchemyFixture
from fixture.style import NamedDataStyle
import oleander.models as models


def install(session, *datasets):
    """Install test data fixtures into the configured database."""
    db_fixture = SQLAlchemyFixture(env=models, style=NamedDataStyle(), session=session)
    data = db_fixture.data(*datasets)
    data.setup()
    session.commit()


class UserData(DataSet):

    class honza:
        name = 'Honza'
        email = 'honza@example.com'
        password_hash = '8358b0f41a589539c6f8d5f36089c82a437f014c'
        password_salt = 'ig9iEWdO3p'
        timezone = 'UTC'

    class zuzejk:
        name = 'Zuzejk'
        email = 'perdas@example.com'
        password_hash = '39c4e794f8aaba7fb388dd6691050de3f06f9e5b'
        password_salt = 'aYf2Ju3uNV'
        timezone = 'Europe/Prague'


class EmailContactData(DataSet):

    class zuzejk:
        name = 'Zuzejk'
        user = UserData.honza
        email = 'perdas@example.com'

    class maple:
        name = 'Maple'
        user = UserData.honza
        email = 'maple@example.com'


class GroupData(DataSet):

    class penoclan:
        name = 'Peno Clan'
        user = UserData.honza
        contacts = [EmailContactData.zuzejk, EmailContactData.maple]


all_data = (
    UserData,
    EmailContactData,
    GroupData,
)
