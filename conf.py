import os

class Config(object):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    FBAPI_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FBAPI_APP_SECRET = os.environ.get('FACEBOOK_SECRET')
    FBAPI_SCOPE = ['user_likes', 'user_photos', 'user_photo_video_tags']
    MONGODB_HOST = "mongodb://heroku_app15232410:6gcfdj39cetjlabuvfv3vpove1@ds061777.mongolab.com:61777/heroku_app15232410"
    MONGODB_DATABASE = "heroku_app15232410"
    # MONGODB_HOST = "localhost"
    # MONGODB_DATABASE = "reversi_db"
    