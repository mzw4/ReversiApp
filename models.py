import re
from datetime import datetime
import pymongo
from pymongo.son_manipulator import AutoReference, NamespaceInjector
from mongokit import Document, Connection, IS

def name_validator(name):
	return True 

# @connection.register
class User(Document):
	__collection__ = 'users'
	__database__ = 'reversi_db'
	structure = {
		'name': basestring,
		'elo_rating': int,
		'wins': int,
		'losses': int,
		'join_date': datetime,
		'sent_challenges': [int],
		'recieved_challenges': [int],
		'current_games': [int],
		'past_games': [int],
		'achievements': [int],
	}
	required_fields = ['name']
	default_values = {
		'elo_rating': 0,
		'wins': 0,
		'losses': 0,
		'sent_challenges': [],
		'recieved_challenges': [],
		'current_games': [],
		'past_games': [],
		'achievements': [],
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
		'white': User,
		'black': User,
		'turn': basestring,
		'white_score': int,
		'black_score': int,
		'completed': bool,
		'timed': bool,
		'size': int,
		'move_list': [{
			'team': basestring,
			'x': int,
			'y': int,
		}],
		'states_list': [[[int]]],	# list of board states, 2d arrays
		'chat_log': basestring,
		'creation_time': datetime,
	}
	required_fields = ['white', 'black', 'timed']
	default_values = {
		'completed': False,
		'size': 8,
		'turn': 'white',
	}
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


# class User(Document):
# 	def __init__(self, name):
# 		self.name = name
# 		self.elo_rating = 0
# 		self.wins = 0
# 		self.losses = 0
# 		self.sent_challenges = []
# 		self.recieved_challenges = []
# 		self.current_games = []
# 		self.past_games = []
# 		self.achievements = []

# 	def __unicode__(self):
# 		return self.name

# 	def get_wl_ratio(self):
# 		return float(wins)/losses

# 	def accept_challenge(self, c_id):
# 		challenge = db.Challenges.get(c_id)
# 		start_game(challenge.reciever, challenge.sender, False)

# class Game:
# 	def __init__(self, p1, p2, timed, size):
# 		self.white = p1
# 		self.black = p2
# 		self.white_score = 0
# 		self.black_score = 0
# 		self.completed = false
# 		self.timed = timed
# 		self.size = size
# 		self.move_list = []
# 		self.states_list = []
# 		self.chat_log = ""
# 		self.turn = ""	# white or black

# class Challenge:
# 	def __init__(self, p1, p2):
# 		self.sender = p1
# 		self.reciever = p2
