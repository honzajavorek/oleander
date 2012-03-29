# -*- coding: utf-8 -*-


#from flask.ext.gravatar import Gravatar
from oleander import app


#gravatar = Gravatar(app, size=50, rating='g', default='mm')


@app.template_filter
def avatar(contact):
    pass
    #if contact.type == 'facebook':
        #return 'https://graph.facebook.com/' + contact.facebook_id + '/picture?type=square'
    #elif contact.type = 'google':
        # http://motyar.blogspot.com/2011/09/fetch-google-plus-profile-picture-using.html
    #else:
    #return gravatar(contact.email)


