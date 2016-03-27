from .common import *

DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '192.198.100.1',
        'PORT': '5432',
    }
}

SECRET_KEY = 'u#3nd=(+sya#!nnrawhrvn!9e0lh(@y3&4^hci=0+sqf%kbtwh'