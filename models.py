import re
from datetime import datetime
import pymongo
from pymongo.son_manipulator import AutoReference, NamespaceInjector
from mongokit import Document, Connection, IS, ObjectId

def name_validator(name):
	return True 

# @connection.register
class User(Document):
	__collection__ = 'users'
	__database__ = 'reversi_db'
	structure = {
		'name': basestring,
		'elo_rating': int,
		'rank': int,
		'wins': int,
		'losses': int,
		'draws': int,
		'join_date': datetime,
		'sent_challenges': [int],
		'received_challenges': [int],
		'current_games': [ObjectId],
		'past_games': [ObjectId],
		'achievements': [int],
	}
	required_fields = ['name']
	default_values = {
		'elo_rating': 0,
		'rank': 0,
		'wins': 0,
		'losses': 0,
		'draws': 0,
		'sent_challenges': [],
		'received_challenges': [],
		'current_games': [],
		'past_games': [],
		'achievements': []
	}
	validators = {
		'name': name_validator,
	}
	use_dot_notation = True

# @connection.register
class Game(Document):
	__collection__ = 'games'
	__database__ = 'reversi_db'
	structure = {
		'_id': ObjectId,
		'white': User,
		'black': User,
		'turn': bool, 	# True = black turn
		'white_score': int,
		'black_score': int,
		'size': int,
		'move_list': [{
			'team': bool,
			'x': int,
			'y': int,
		}],
		'states_list': [[[int]]],	# list of 2d array board states
		# states_list: -1 is empty, 0 is white, 1 is black
		'chat_log': [basestring],       # 1D array of strings
		'creation_time': datetime,
		'end_time': datetime,
		'completed': bool,
		'winner': {
			'id': int,
			'name': basestring,
		}

	}
	required_fields = ['white', 'black']
	default_values = {
		'_id': ObjectId(),
		'turn': False,
		'white_score': 2,
		'black_score': 2,
		'size': 8,
		'move_list': [],
		'states_list': [[[-1]*8,[-1]*8,[-1]*8,[-1,-1,-1,0,1,-1,-1,-1],[-1,-1,-1,1,0,-1,-1,-1],[-1]*8,[-1]*8,[-1]*8]],
		'chat_log': [],
		'completed': False
	}
	use_dot_notation = True
	use_autorefs = True

# class Session(Document):
# 	__collection__ = 'sessions'
# 	__database__ = 'reversi_db'
# 	structure = {
# 		'user': User,
# 		'token': basestring,
# 		'fb_user': basestring,
# 	}
# 	required_fields = ['user', 'token']
# 	use_dot_notation = True
# 	use_autorefs = True

class PlayRequest(Document):
	__collection__ = 'play_requests'
	__database__ = 'reversi_db'
	structure = {
		'user': User,
	}
	required_fields = ['user']
	use_dot_notation = True
	use_autorefs = True

# @connection.register
class Challenge(Document):
	__collection__ = 'challenges'
	__database__ = 'reversi_db'
	structure = {
		'sender': User,
		'receiver': User,
	}
	required_fields = ['sender', 'receiver']
	use_dot_notation = True
	use_autorefs = True
