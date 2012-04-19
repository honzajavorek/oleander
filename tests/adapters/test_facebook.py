# -*- coding: utf-8 -*-


try:
    import unittest2 as unittest
except ImportError:
    import unittest


from oleander.adapters import DependencyError
from oleander.adapters.facebook import FacebookAdapter
import urlparse


try:
    import requests
except ImportError:
    raise DependencyError("Facebook adapter requires 'requests' (github.com/kennethreitz/requests).")


class TestFacebookAdapter(unittest.TestCase):

    app_id = ''
    app_secret = ''

    # https://developers.facebook.com/roadmap/offline-access-removal/
    user_access_token = ''

    @property
    def app_access_token(self):
        response = requests.get('https://graph.facebook.com/oauth/access_token', params=dict(
            client_id=self.app_id,
            client_secret=self.app_secret,
            grant_type='client_credentials'
        ))
        return urlparse.parse_qs(response.text)['access_token']

    @unittest.skipUnless(app_id, "No Facebook 'app ID' defined.")
    @unittest.skipUnless(app_secret, "No Facebook 'app secret' defined.")
    @unittest.skipUnless(user_access_token, "No Facebook 'user access token' defined. Use developers.facebook.com/tools/explorer/ to acquire one.")
    def test_get_contacts(self):
        a = FacebookAdapter(self.user_access_token)
        list(a.contacts)


if __name__ == '__main__':
    unittest.main()