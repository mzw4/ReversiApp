/*** GLOBAL VARIABLES (NECESSARY) ***/
var currentGame;
var states_list_length;
var states_list_array;

$(document).ready(function() {

	states_list_array = $("#states_list_array").text();
	states_list_length = $("#states_list_length").text();

	currentGame = states_list_length - 1;

	// Render the game board
	renderBoard($(".board_history"));

	// Display the last game state
	displayGame(currentGame);

	// Activate game-state navigation
	activateStateNav();
});

// MAIN FUNCTION
// - for setting up game-state navigation
function activateStateNav() {
	console.log("Reached the start of activateStateNav()");
	$("a.earlier_state").on("click", function() {
		changeGameState(-1);
	});

	$("a.later_state").on("click", function() {
		changeGameState(1);
	});
}

// HELPER FUNCTION
// - for changing out game-states, based off an $incr
function changeGameState($incr) {
	console.log("Reached changeGameState()");
	console.log("States_list_length: " + states_list_length);
	if ($incr == -1 && currentGame > 0) { // good current state
		console.log("Reached changeGameState(-1)");
		currentGame--;
		displayGame(currentGame);
	} else if ($incr == 1 && currentGame < states_list_length - 1) { // good current state
		console.log("Reached changeGameState(1)");
		currentGame++;
		displayGame(currentGame);
	} else { // bad current state
		console.log("Reached changeGameState() at a bad state");
		return false;
	}
	$("#current_state").text(currentGame+1);
}

// $index: the index representing the appropriate game state,
// from the array: states_list_array
function displayGame($index) {
	console.log("Reached displayGame()");
	$thisGame = states_list_array[$index];
	
	for ($i = 0; $i < 8; $i++) {
		for ($j = 0; $j < 8; $j++) {
			switch ($thisGame[$i][$j]) {
				case -1:
					togglePiece($i, $j, "empty");
					break;
				case 0:
					togglePiece($i, $j, "white");
					break;
				case 1:
					togglePiece($i, $j, "black");
					break;
			}
		}
	}
}

function renderBoard($gameboard) {
	for ($x = 0; $x < 8; $x++) {
		$gameboard.append("<div class='row_wrapper X_"+$x+"'></div>");
		$tempRow = $("div.X_"+$x);
		for ($y = 0; $y < 8; $y++) {
			$tempRow.append("<a href='javascript:void(0)' class='boardspot empty X_"+$x+" Y_"+$y+"'></a>");
		}
	} 
} 

// HELPER FUNCTION
// - for toggling boardspots to black or white
function togglePiece($x, $y, $blackorwhite) {
	$boardspot = $(".X_"+$x+".Y_"+$y);
	if ($blackorwhite == "white") {
		$boardspot.toggleClass("white", true);
		$boardspot.toggleClass("black", false); 
		$boardspot.toggleClass("empty", false);
	} else if ($blackorwhite == "black") {
		$boardspot.toggleClass("black", true);
		$boardspot.toggleClass("white", false);
		$boardspot.toggleClass("empty", false);
	} else if ($blackorwhite == "empty") {
		$boardspot.toggleClass("empty", true);
		$boardspot.toggleClass("white", false);
		$boardspot.toggleClass("black", false);
	}
}
