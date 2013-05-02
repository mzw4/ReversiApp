from datetime import datetime

# starts a game instance between specified players p1 and p2
# returns the game
def start_game(p1, p2, timed):
	game = db.Game()
	game.white = p1
	game.black = p2
	game.timed = timed
	game.creation_time = datetime.now()
	p1.current_games.append(game.id)
	p2.current_games.append(game.id)
	return game

# ends a game instance and returns the winner
# in the case of a tie, returns None
def end_game(game):
	white =game.white
	black = game.black

	white.current_games.remove(game.id)
	black.current_games.remove(game.id)
	white.past_games.append(game.id)
	black.past_games.append(game.id)

	game.completed = True

	if game.white_score > game.black_score:
		return white['id']
	elif game.black_score > game.white_score:
		return black['id']
	else:
		return None

# ends a game instance
def forfeit(game, player):
	white =game.white
	black = game.black

	white.current_games.remove(game.id)
	black.current_games.remove(game.id)
	white.past_games.append(game.id)
	black.past_games.append(game.id)

	game.completed = True

	if white.id == player.id:
		return black['id']
	else:
		return white['id']


def perform_move(game, y, x):
	if game.turn == "white":
		piece = 0 # white
	else:
		piece = 1 # black

	if game.states_list: # ensures states_list is not empty
		state = game.states_list[-1] # current board state
	else:
		return False
	# validate move
	if not validate_move(state, y, x, piece):
		return False
	# update moves list
	game.moves_list.append({ 'team': game.turn, 'x': x, 'y': y})
	#place piece
	state[y][x] = piece

	# check_range(y-1, -1, True, "N") # N
	# check_range(y+1, len(state), False, "S") # S
	# check_range(x+1, len(state[y]), False, "E") # E
	# check_range(x-1, -1, True, "W") # W			

	# check_range(y-1, -1, False, "NE") # NE			
	# check_range(y-1, -1, True, "NW") # NW			
	# check_range(y+1, len(state), False, "SE") # SE			
	# check_range(y+1, len(state), True, "SW") # SW			

	for i in range(y-1, -1, -1): # N
		if state[i][x] == piece:
			toggle(y-1, i, "N")
			break

	for i in range(y+1, len(state)): # S
		if state[i][x] == piece:
			toggle(y+1, i, "S")
			break

	for i in range(x+1, len(state[y])): # E
		if state[y][i] == piece:
			toggle(x+1, i, "E")
			break

	for i in range(x-1, -1, -1): # W
		if state[y][i] == piece:
			toggle(x-1, i, "W")
			break

	xoffset = 0
	for i in range(y-1, -1, -1): # NE
		xoffset += 1
		if state[i][x+xoffset] == piece:
			toggle(y-1, i, "NE")
			break

	xoffset = 0
	for i in range(y-1, -1, -1): # NW
		xoffset -= 1
		if state[i][x+xoffset] == piece:
			toggle(y-1, i, "NW")
			break

	xoffset = 0
	for i in range(y+1, len(state)): # SE
		xoffset += 1
		if state[i][x+xoffset] == piece:
			toggle(y+1, i, "SE")
			break

	xoffset = 0
	for i in range(y+1, len(state)): # SW
		xoffset -= 1
		if state[i][x+xoffset] == piece:
			toggle(y+1, i, "SW")
			break

	game.states_list.append(state)
	return True

	# def check_range(start, end, desc, dir):
	# 	if dir == "NW" || dir == "NE" || dir == "SW" || dir == "SE": 
	# 		xoffset = 0
	# 		for i in range(start, end)
	# 			if desc: 			# NW/SW
	# 				xoffset -= 1
	# 			else: 				# NE/SE
	# 				xoffset += 1
	# 			if state[i][x+xoffset] == piece:
	# 				toggle(y, x, i, x+xoffset)
	# 				break
	# 	elif desc: 					
	# 		for i in range(start, -1, end):
	# 			if dir == "N": 		# N
	# 				if state[i][x] == piece:
	# 					toggle(y, x, i, x)
	# 					break
	# 			else: 				# W
	# 				if state[y][i] == piece:
	# 					toggle(y, x, y, i)
	# 					break
	# 	else: 						
	# 		for i in range(start, end):
	# 			if dir == "S":
	# 				if state[i][x] == piece:
	# 					toggle(y, x, i, x)
	# 					break
	# 			else:
	# 				if state[y][i] == piece:
	# 					toggle(y, x, y, i)
	# 					break

	# flips all the pieces in a line from the given
	# start coordinates up to the finish coordinates
	def toggle(start, end, dir):
		if dir == "N":
			for i in range(start, -1, end):
				state[i][x] = state[i][x] ^ 1
		elif dir == "S":
			for i in range(start, end):
				state[i][x] = state[i][x] ^ 1
		elif dir == "E":
			for i in range(start, end):
				state[y][i] = state[y][i] ^ 1
		elif dir == "W":
			for i in range(start, -1, end):
				state[y][i] = state[y][i] ^ 1
		elif dir == "NE":
			xoffset = 0
			for i in range(start, -1, end): # NE
				xoffset += 1
				state[i][x+xoffset] = state[i][xoffset] ^ 1
		elif dir == "NW":
			xoffset = 0
			for i in range(start, -1, end): # NW
				xoffset -= 1
				state[i][x+xoffset] = state[i][xoffset] ^ 1
		elif dir == "SE":
			xoffset = 0
			for i in range(start, end): # SE
				xoffset += 1
				state[i][x+xoffset] = state[i][xoffset] ^ 1
		else:
			xoffset = 0
			for i in range(start, end): # SW
				xoffset -= 1
				state[i][x+xoffset] = state[i][xoffset] ^ 1

	def validate_move(state, y, x, piece):
		if state[y][x] != -1 or y >= game.size or y < 0 or \
			x >= game.size or x < 0:
			return False

		valid = False
		if y > 0 and state[y-1][x] == (piece ^ 1):				# N
			for i in range (y-1, -1, -1):
				if state[i][x] == piece:
					valid = True
					break
				elif state[i][x] == -1:
					valid = False
					break
		if y < game.size-1 and state[y+1][x] == (piece ^ 1):		# S
			for i in range (y+1, game.size):
				if state[i][x] == piece:
					valid = True
		if x < game.size-1 and state[y][x+1] == (piece ^ 1):		# E
			for i in range (x+1, game.size):
				if state[y][i] == piece:
					valid = True
		if x > 0 and state[y][x-1] == (piece ^ 1):				# W
			for i in range (x-1, -1, -1):
				if state[y][i] == piece:
					valid = True
		if x > 0and y > 0 and state[y-1][x+1] == (piece ^ 1):	# NE
			xoffset = 0
			for i in range (y-1, -1, -1):
				xoffset += 1
				if state[i][x+xoffset] == piece:
					valid = True
		if x > 0 and y > 0 and state[y-1][x+1] == (piece ^ 1):	# NE
			xoffset = 0
			for i in range (y-1, -1, -1):
				xoffset -= 1
				if state[i][x+xoffset] == piece:
					valid = True

def update_scores(game):
	if game.states_list: 	# ensure states_list is not empty
		state = game.states_list[-1]

	white_score = 0
	black_score = 0

	for i in range(len(state)):
		for j in range(len(state[i])):
			if state[i][j] == 0:
				white_score += 1
			elif state[i][j] == 1:
				black_score += 1

	game.white_score = white_score
	game.black_score = black_score