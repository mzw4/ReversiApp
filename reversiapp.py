# -*- coding: utf-8 -*-

import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime

# framework imports
import pymongo
from pymongo.son_manipulator import AutoReference, NamespaceInjector
# from pymongo import MongoClient
import requests
from flask import Flask, session, request, redirect, render_template, url_for, g
from flask.ext.mongokit import MongoKit, Document
from mongokit import ObjectId
# from flask.ext.pymongo import PyMongo

# app imports
from models import User, Game, Challenge, PlayRequest
import game_controller

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = requests.session()

app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
FB_APP_SECRET = os.environ.get('FACEBOOK_SECRET')

current_user = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')

app.secret_key = '\x92\xaa\x81l\x10m\x8c\x97\xc1\xd7\x93\x95\xb9\xfbrC\xf9\xff:~D\xbf\x97\x86'

# app.config["MONGODB_DATABASE"] = DB_NAME
# app.config["MONGODB_HOST"] = MONGODB_URI

db = MongoKit(app)
db.register([User, Game, PlayRequest, Challenge])
# db.users.drop()

# try:
#     connection = pymongo.Connection(MONGODB_URI)
#     db = connection[DB_NAME]
# except:
#     print('Error: Unable to connect to database')
#     connection = None

# if connection is not None:
#     db.pokemon.insert({"name": "Pika"})

# app.config['MONGO_URI'] = "mongodb://heroku_app15232410:6gcfdj39cetjlabuvfv3vpove1@ds061777.mongolab.com:61777/heroku_app15232410"
# mongo = PyMongo(app
# mongo.db.pokemon.insert({name: "Pika"})

def oauth_login_url(preserve_path=True, next_url=None):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s" %
                    (app.config['FB_APP_ID'], get_home()))

    if app.config['FBAPI_SCOPE']:
        fb_login_uri += "&scope=%s" % ",".join(app.config['FBAPI_SCOPE'])
    return fb_login_uri


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def fbapi_get_string(path,
    domain=u'graph', params=None, access_token=None,
    encode_func=urllib.urlencode):
    """Make an API call"""

    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    result = requests.get(url).content

    return result


def fbapi_auth(code):
    params = {'client_id': app.config['FB_APP_ID'],
              'redirect_uri': get_home(),
              'client_secret': app.config['FB_APP_SECRET'],
              'code': code}

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)
    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    return (result_dict["access_token"], result_dict["expires"])


def fbapi_get_application_access_token(id):
    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials', client_id=id,
                    client_secret=app.config['FB_APP_SECRET']),
        domain=u'graph')

    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token


def fql(fql, token, args=None):
    if not args:
        args = {}

    args["query"], args["format"], args["access_token"] = fql, "json", token

    url = "https://api.facebook.com/method/fql.query"

    r = requests.get(url, params=args)
    return json.loads(r.content)


def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    return json.loads(r.content)

def get_home():
    return 'https://' + request.host + '/'

def get_token():

    if request.args.get('code', None):
        return fbapi_auth(request.args.get('code'))[0]

    cookie_key = 'fbsr_{0}'.format(FB_APP_ID)

    if cookie_key in request.cookies:

        c = request.cookies.get(cookie_key)
        encoded_data = c.split('.', 2)

        sig = encoded_data[0]
        data = json.loads(urlsafe_b64decode(str(encoded_data[1]) +
            (64-len(encoded_data[1])%64)*"="))

        if not data['algorithm'].upper() == 'HMAC-SHA256':
            raise ValueError('unknown algorithm {0}'.format(data['algorithm']))

        h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
        h.update(encoded_data[1])
        expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')

        if sig != expected_sig:
            raise ValueError('bad signature')

        code =  data['code']

        params = {
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'redirect_uri': '',
            'code': data['code']
        }

        from urlparse import parse_qs
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        token = parse_qs(r.content).get('access_token')

        return token

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'token' in app.config:
        access_token = app.config['token']
    else:
        access_token = get_token()

    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    if access_token:
        current_user = db.users.find_one({'_id': session['uid']}, 'as_class'=User)
        # current_user = app.config['user']
        if not current_user:
            return redirect(url_for('login'))

        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})

        redir = get_home() + 'close/'
        POST_TO_WALL = ("https://www.facebook.com/dialog/feed?redirect_uri=%s&"
                        "display=popup&app_id=%s" % (redir, FB_APP_ID))

        app_friends = fql(
            "SELECT uid, name, is_app_user, pic_square "
            "FROM user "
            "WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) AND "
            "  is_app_user = 1", access_token)

        SEND_TO = ('https://www.facebook.com/dialog/send?'
                   'redirect_uri=%s&display=popup&app_id=%s&link=%s'
                   % (redir, FB_APP_ID, get_home()))

        url = request.url

        # # update current_user - should probably be done at login
        current_user = db.users.find_one({'_id': me['id']})
        if not current_user:
            current_user = db.User()
            current_user['_id'] = me['id']
            current_user['name'] = me['name']
            current_user.save()

        # update online_users collection
        db.online_users.insert(current_user)

        user_friends = []
        for f in app_friends:
            friend = db.users.find_one({'_id': f['uid']})
            if friend:
                db.online_users.insert(friend)
                user_friends.append(friend)

        online_friends = []
        me = db.online_users.find_one({'_id': current_user['_id']})
        online_friends.append(me)
        for f in user_friends:
            if db.online_users.find_one({'_id': f['_id']}):
                online_friends.append(f)

        u1 = db.User()
        u1['name'] = "Dummy User"
        u2 = db.User()
        u2['name'] = "Another Dummy"
        u2['_id'] = 12345
        u3 = db.User()
        u3['name'] = "Edward the Dastardly"
        u4 = db.User()
        u4['name'] = "Batman"
        u4['_id'] = 12344           
        u5 = db.User()
        u5['name'] = "Pikachu"
        u5['_id'] = 12343
        u6 = db.User()
        u6['name'] = "Sauron"
        u6['_id'] = 12342
        # online_friends.append(u1)
        # online_friends.append(u2)
        # online_friends.append(u3)

        recent_games = []
        g1 = db.Game()
        g1['white'] = u1
        g1['black'] = current_user
        g1['timed'] = False
        g1['winner_id'] = current_user['_id']
        g2 = db.Game()
        g2['white'] = current_user
        g2['black'] = u2
        g2['timed'] = False
        g2['winner_id'] = u2['_id']
        g3 = db.Game()
        g3['white'] = current_user
        g3['black'] = u3
        g3['timed'] = False
        g3['winner_id'] = current_user['_id']
        g4 = db.Game()
        g4['white'] = current_user
        g4['black'] = u4
        g4['timed'] = False
        g4['winner_id'] = u4['_id']
        g5 = db.Game()
        g5['white'] = current_user
        g5['black'] = u5
        g5['timed'] = False
        g5['winner_id'] = u5['_id']
        g6 = db.Game()
        g6['white'] = current_user
        g6['black'] = u6
        g6['timed'] = False
        g6['winner_id'] = u6['_id']
        recent_games.append(g1)
        recent_games.append(g2)
        recent_games.append(g3)
        recent_games.append(g4)
        recent_games.append(g5)
        recent_games.append(g6)


        for gid in current_user['current_games']:
            g = db.games.find_one({'_id':gid})
            if g:
                recent_games.append(g)

        num_games = len(recent_games)
        num_online_friends = len(online_friends)

        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token,
            app_friends=app_friends, app=fb_app,
            user_friends=user_friends, online_friends=online_friends,
            num_online_friends=num_online_friends,
            me=me, current_user=current_user,
            recent_games=recent_games, num_games=num_games,
            POST_TO_WALL=POST_TO_WALL, SEND_TO=SEND_TO,
            url=url, channel_url=channel_url, name=FB_APP_NAME)
    else:
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)
    # current_user = app.config['user']

    if access_token and current_user:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        url = request.url

        num_games = len(current_user['past_games'])

        return render_template(
            'profile.html', app_id=FB_APP_ID, token=access_token,
            num_games=num_games, me=me, current_user=current_user,
            url=url, name=FB_APP_NAME)
    else:
        return redirect(url_for('login'))

@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)
    # current_user = app.config['user']

    if access_token and current_user:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        url = request.url

        game = db.games.find_one({'_id': game_id})
        # if the game is not valid, redirect to home page
        if not game:
            return redirect(url_for('home'))

        # determine if the game has just started
        just_started = len(game['states_list']) <= 2
        # current game board is the latest state in states_list
        current_board = game['states_list'][-1]

        # determine turn and score
        if game['turn'] and game['black']['_id'] == current_user['_id']:
            turn = True
            player_score = game['black_score']
            opponent_score = game['white_score']
        else:
            turn = False
            player_score = game['white_score']
            opponent_score = game['black_score']

        return render_template('game.html', game=game,
            turn=turn, just_started=just_started,
            player_score=player_score, opponent_score=opponent_score,
            me=me, current_user=current_user, opponent=opponent,
            app_id=FB_APP_ID, token=access_token, app=fb_app,
            url=url, name=FB_APP_NAME, board=current_board)
    else:
        return redirect(url_for('login'))

@app.route('/quickplay', methods=['GET', 'POST'])
def quickplay():
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)
    # current_user = app.config['user']

    if access_token and current_user:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        url = request.url

        # find an opponent requesting a game
        db.play_requests.remove()
        opponent_request = db.play_requests.find_one()

        if opponent_request:
            # start a game with an opponent
            opponent = opponent_request['user']
            # game = start_game(current_user, opponent)
            game = db.Game()
            game['white'] = current_user
            game['black'] = opponent
            game.creation_time = datetime.now()
            current_user['current_games'].append(game['_id'])
            opponent['current_games'].append(game['_id'])
            game.save()
            return redirect(url_for('game', game_id=game['_id']))
        # else:
        #     # request a game with the server
        #     pr = db.PlayRequest()
        #     pr['user'] = current_user
        #     pr.save()
        #     need to somehow nofity user by pop up that play request has been made
        #     return redirect(url_for('home'))

        # -- dummy data
        opponent_dummy = db.User()
        opponent_dummy['name'] = 'Ed'
        opponent_dummy['_id'] = 12345
        opponent_dummy.save()
        opponent = opponent_dummy

        db.games.remove()
        game = db.Game()
        game['white'] = current_user
        game['black'] = opponent_dummy
        current_user['current_games'].append(game['_id'])
        opponent_dummy['current_games'].append(game['_id'])
        game.save()

        return redirect(url_for('game', game_id=game['_id']))
        # -- dummy data

    else:
        return redirect(url_for('login'))

@app.route('/move/<game_id>/<x>/<y>', methods=['GET', 'POST'])
def make_move(game_id, x, y):
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)

    if access_token:
        game = db.games.find_one({'_id': game_id}, as_class=Game)
        perform_move(game, x, y)
        update_scores(game)
        game.save()

        return redirect(url_for('game', game_id=game_id))
    else:
        return redirect(url_for('home'))




@app.route('/game_history', methods=['GET', 'POST'])
def game_history():
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)
    # current_user = session['user']

    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        url = request.url

        past_games = []
        for gid in current_user['past_games']:
            game = db.games.find_one({'_id': gid})
            if game:
                past_games.append(game)
        
        return render_template(
            'game_history.html', past_games=past_games,
            app_id=FB_APP_ID, token=access_token,
            app=fb_app, me=me, current_user=current_user,
            url=url, name=FB_APP_NAME)
    else:
        return redirect(url_for('login'))

@app.route('/game_stats/<game_id>', methods=['GET', 'POST'])
def game_stats(game_id):
    access_token = app.config['token']
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')
    current_user = db.users.find_one({'_id': session['uid']}, as_class=User)
    # current_user = session['user']

    if 'token' in app.config and app.config['token']:
    # if access_token:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        url = request.url

        game = db.games.find_one({'_id': game_id})
        if not game:
            return redirect(url_for('game_history'))

        return render_template(
            'game_stats.html', game=game,
            app_id=FB_APP_ID, token=access_token,
            app=fb_app, me=me, current_user=current_user,
            url=url, name=FB_APP_NAME)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    # # --temp
    db.users.remove()

    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})

        # update current_user
        current_user = db.users.find_one({'_id': me['id']})
        if not current_user:
            current_user = db.User()
            current_user['_id'] = me['id']
            current_user['name'] = me['name']
            # -- dummy data
            current_user['past_games'] = [ObjectId(),ObjectId(),ObjectId(),ObjectId()]
            current_user['wins'] = 12345
            current_user['losses'] = 12345
            # -- dummy data
            current_user.save()

        session['uid'] = current_user['_id']
        app.config['token'] = access_token

        return redirect(url_for('home'))
    else:
        return render_template('login.html', app_id=FB_APP_ID,
         token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/logout')
def logout():
    session.pop('uid', None)
    app.config.pop('token', None)
    return render_template('login.html', app_id=FB_APP_ID,
     token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if app.config.get('FB_APP_ID') and app.config.get('FB_APP_SECRET'):
        app.run(host='0.0.0.0', port=port)
    else:
        print 'Cannot start application without Facebook App Id and Secret set'
