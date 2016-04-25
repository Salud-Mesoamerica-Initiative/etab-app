import os

from .common import *

DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'orchid',
        'USER': 'postgres',
        'PASSWORD': 'r4ss1n1gg',
        'HOST': 'mohtestdb.cqvqhvonzmwu.us-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

SECRET_KEY = 'u#3nd=(+sya#!nnrawhrvn!9e0lh(@y3&4^hci=0+sqf%kbtwh'

ALLOWED_HOSTS = ['*']

AWS_SECRET_ACCESS_KEY = os.environ.get('ORCHID_AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('ORCHID_AWS_ACCESS_KEY_ID')
AWS_STORAGE_BUCKET_NAME = os.environ.get('ORCHID_AWS_STORAGE_BUCKET_NAME')

CELERYCONF = {
    'CELERY_ALWAYS_EAGER': True,
    'BROKER_URL': 'amqp://guest:guest@localhost:5672//'
}
