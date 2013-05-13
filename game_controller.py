from datetime import datetime

# starts a game instance between specified players p1 and p2
# returns the game
def start_game(p1, p2):
	game = db.Game()
	game.white = p1
	game.black = p2
	game.creation_time = datetime.now()
	p1.current_games.append(game.id)
	p2.current_games.append(game.id)
	return game

# ends a game instance and returns the winner
# in the case of a tie, returns None
def end_game(game):
	white = game.white
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
	white = game.white
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


# note: function only called if it is user's turn
def perform_move(game, y, x):
	piece = int(game.turn)

	state = game.states_list[-1] # current board state

	# validate move
	if not validate_move(state, y, x, piece):
		return None
	# update moves list
	game.moves_list.append({'team': game.turn, 'x': x, 'y': y})
	# place piece
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
			toggle(y, i, "N")
			break

	for i in range(y+1, len(state)): # S
		if state[i][x] == piece:
			toggle(y, i, "S")
			break

	for i in range(x+1, len(state[y])): # E
		if state[y][i] == piece:
			toggle(x, i, "E")
			break

	for i in range(x-1, -1, -1): # W
		if state[y][i] == piece:
			toggle(x, i, "W")
			break

	xoffset = 0
	for i in range(y-1, -1, -1): # NE
		xoffset += 1
		if x+xoffset >= len(state):
			break
		if state[i][x+xoffset] == piece:
			toggle(y, i, "NE")
			break

	xoffset = 0
	for i in range(y-1, -1, -1): # NW
		xoffset -= 1
		if x+xoffset <= 0:
			break
		if state[i][x+xoffset] == piece:
			toggle(y, i, "NW")
			break

	xoffset = 0
	for i in range(y+1, len(state)): # SE
		xoffset += 1
		if x+xoffset >= len(state):
			break
		if state[i][x+xoffset] == piece:
			toggle(y, i, "SE")
			break

	xoffset = 0
	for i in range(y+1, len(state)): # SW
		xoffset -= 1
		if x+xoffset <= 0:
			break
		if state[i][x+xoffset] == piece:
			toggle(y, i, "SW")
			break

	game.states_list.append(state)
	update_scores(game)

	white_moves = possible_moves(state, 0)
	black_moves = possible_moves(state, 1)

	if not white_moves and not black_moves:
		end_game(game)
	elif not white_moves:
		game.turn = True
	elif not black_moves:
		game.turn = False
	else:
		game.turn = not game.turn

	return game

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
# start coordinates up to the finish coordinates (EXCLUSIVE!!!)
def toggle(start, end, direction):
	if direction == "N":
		for i in range(start-1, end, -1):
			state[i][x] = state[i][x] ^ 1
	elif direction == "S":
		for i in range(start+1, end):
			state[i][x] = state[i][x] ^ 1
	elif direction == "E":
		for i in range(start+1, end):
			state[y][i] = state[y][i] ^ 1
	elif direction == "W":
		for i in range(start-1, end, -1):
			state[y][i] = state[y][i] ^ 1
	elif direction == "NE":
		xoffset = 0
		for i in range(start-1, end, -1): # NE
			xoffset += 1
			state[i][x+xoffset] = state[i][x+xoffset] ^ 1
	elif direction == "NW":
		xoffset = 0
		for i in range(start-1, end, -1): # NW
			xoffset -= 1
			state[i][x+xoffset] = state[i][x+xoffset] ^ 1
	elif direction == "SE":
		xoffset = 0
		for i in range(start+1, end): # SE
			xoffset += 1
			state[i][x+xoffset] = state[i][x+xoffset] ^ 1
	else:
		xoffset = 0
		for i in range(start+1, end): # SW
			xoffset -= 1
			state[i][x+xoffset] = state[i][x+xoffset] ^ 1


def validate_move(state, y, x, piece):
	if y >= len(state) or y < 0 or x >= len(state) or x < 0 \
		    or state[y][x] != -1:
		return False
	
	if y > 0 and state[y-1][x] == (piece ^ 1): # N
		for i in range (y-2, -1, -1):
			if state[i][x] == piece:
				return True
			elif state[i][x] == -1:
				break
	if y < len(state)-1 and state[y+1][x] == (piece ^ 1): # S
		for i in range (y+2, len(state)):
			if state[i][x] == piece:
				return True
			elif state[i][x] == -1:
				break
	if x < len(state)-1 and state[y][x+1] == (piece ^ 1): # E
		for i in range (x+2, len(state)):
			if state[y][i] == piece:
				return True
			elif state[y][i] == -1:
				break
	if x > 0 and state[y][x-1] == (piece ^ 1): # W
		for i in range (x-2, -1, -1):
			if state[y][i] == piece:
				return True
			elif state[y][i] == -1:
				break
	if x < len(state)-1 and y > 0 \
		    and state[y-1][x+1] == (piece ^ 1): # NE
		xoffset = 1
		for i in range (y-2, -1, -1):
			xoffset += 1
			if state[i][x+xoffset] == piece:
				return True
			elif state[i][x+xoffset] == -1:
				break
	if x > 0 and y > 0 and state[y-1][x-1] == (piece ^ 1): # NW
		xoffset = -1
		for i in range (y-2, -1, -1):
			xoffset -= 1
			if state[i][x+xoffset] == piece:
				return True
			elif state[i][x+xoffset] == -1:
				break;
	if x < len(state)-1 and y < len(state)-1 \
		    and state[y+1][x+1] == (piece ^ 1): # SE
		xoffset = 1
		for i in range(y+2, len(state)):
			xoffset += 1
			if state[i][x+xoffset] == piece:
				return True
			elif state[i][x+xoffset] == -1:
				break
	if x > 0 and y < len(state)-1 \
		    and state[y+1][x-1] == (piece ^ 1): # SW
		xoffset = -1
		for i in range(y+2, len(state)):
			xoffset -= 1
			if state[i][x+xoffset] == piece:
				return True
			elif state[i][x+xoffset] == -1:
				break
	return False


def possible_moves(state, piece):
	count = 0
	for r in range(0, len(state)):
		for c in range(0, len(state)):
			if validate_move(state, r, c, piece):
				count += 1
	return count


def update_scores(game):
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


# for development only:
def print_board(state):
	for r in range(len(state)):
		buffer = ""
		for c in range(len(state)):
			buffer += `state[r][c]` + " "
		print(buffer+"\n")
