# -*- coding: utf-8 -*-


from fixture import DataSet, SQLAlchemyFixture
from fixture.style import NamedDataStyle
import oleander.models as models
import times
from datetime import timedelta


def install(session, *datasets):
    """Install test data fixtures into the configured database."""
    db_fixture = SQLAlchemyFixture(env=models, style=NamedDataStyle(), session=session)
    data = db_fixture.data(*datasets)
    data.setup()


# emails are rot13 encoded not to be readable by spamming bots
# (who knows where this source code can appear once)


now = times.now()


class UserData(DataSet):

    class honza:
        name = 'Honza'
        email = 'ubamn@wniberx.arg'.decode('rot13')
        password_hash = '8358b0f41a589539c6f8d5f36089c82a437f014c'
        password_salt = 'ig9iEWdO3p'
        timezone = 'UTC'

    class zuzejk:
        name = 'Zuzejk'
        email = 'creqnf@frmanz.pm'.decode('rot13')
        password_hash = '39c4e794f8aaba7fb388dd6691050de3f06f9e5b'
        password_salt = 'aYf2Ju3uNV'
        timezone = 'Europe/Prague'


class EmailContactData(DataSet):

    class zuzejk:
        name = 'Zuzejk'
        user = UserData.honza
        email = 'creqnf@frmanz.pm'.decode('rot13')

    class maple:
        name = 'Maple'
        user = UserData.honza
        email = 'zncyr@frmanz.pm'.decode('rot13')

    class vasar:
        name = 'Vasar'
        user = UserData.honza
        email = 'infne@frmanz.pm'.decode('rot13')

    class milan:
        name = u'Milča'
        user = UserData.honza
        email = 'zxbyvafxl@pragehz.pm'.decode('rot13')


class GoogleContactData(DataSet):

    class peta:
        name = u'Peťa'
        user = UserData.honza
        email = 'cna.inpun@tznvy.pbz'.decode('rot13')

    class misa:
        name = u'Míša'
        user = UserData.honza
        email = 'cna.firp@tznvy.pbz'.decode('rot13')

    class baki:
        name = 'Baki'
        user = UserData.honza
        email = 'cna.onxrf@tznvy.pbz'.decode('rot13')

    class ja:
        name = 'Honza'
        user = UserData.honza
        email = 'wna.wniberx@tznvy.pbz'.decode('rot13')


class EventData(DataSet):

    class happyevent:
        name = u'Happy Event'
        description = u'Happy event for happy people!'
        venue = models.Venue(name='Kaverna, Brno', lat=49.19921, lng=16.60208)
        user = UserData.honza
        created_at = now
        updated_at = now
        starts_at = now + timedelta(days=5, hours=5)


all_data = (
    UserData,
    EmailContactData,
    GoogleContactData,
    EventData,
)
