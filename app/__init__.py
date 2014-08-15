import os
import re
import time
import json
import string
import requests
import datetime

import logging
import logging.config

from functools import wraps
from pymongo import Connection
from urllib import URLopener

from flask import Flask
from flask import session
from flask import g
from flask import request
from flask import url_for
from flask import render_template
from flask import redirect
from flask_oauth import OAuth


#=========================================================================
# CONFIGURE APP
#=========================================================================
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.urandom(24)

oauth = OAuth()
facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=app.config['FACEBOOK_APP_ID'],
                            consumer_secret=app.config['FACEBOOK_APP_SECRET'],
                            request_token_params={'scope': 'user_photos,friends_photos'}
                            )


#=========================================================================
# LOGGER
#=========================================================================
logger = logging.getLogger('%s' % 'APP')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s | %(message)s',
            'datefmt': '%H:%M:%S',
        },
        'verbose': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        #'filelog': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': os.path.join(app.config['BASE_PATH'], 'APP.log'),
        #    'formatter': 'verbose'
        #},
    },
    'loggers': {
        'werkzeug': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': True,
        },
        'APP': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
logging.config.dictConfig(LOGGING)


#=========================================================================
# LAUNCH
#=========================================================================
def start_app():
    app.run()


import views
