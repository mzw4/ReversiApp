// Assumes jQuery

// BEGIN
$(document).ready(begin);

// MASTER FUNCTION
// - for doing EVERYTHING
function begin() {
	// Create pointer for gameboard DOM element
	$gameboard = $("div.gameboard");

	renderBoard($gameboard);
	setUpReversi();
	activateBoardSpots();
}

// MAIN FUNCTION
// - for rendering the game board
// Properly renders each board spot, with the appropriate class types for rows,
// columns, game piece type, and anything else we would need
// $gameboard: DOM element to which we append the gameboard
function renderBoard($gameboard) {
	console.log("Reached the start of renderBoard()");
	console.log("Begin appending boardspots");
	for ($x = 0; $x < 8; $x++) {
		$gameboard.append("<div class='row_wrapper X_"+$x+"'></div>");
		$tempRow = $("div.X_"+$x);
		for ($y = 0; $y < 8; $y++) {
			$tempRow.append("<a href='javascript:void(0)' class='boardspot empty X_"+$x+" Y_"+$y+"'></a>");
		}
	} 
	console.log("Reached the end of renderBoard()");
} 

// MAIN FUNCTION
// - for properly setting up the game board
// White pieces at (3,3) and (4,4)
// Black pieces at (3,4) and (4,3)
function setUpReversi() {
	console.log("Reached the start of setUpReversi()");
	// Set the white pieces
	togglePiece(3, 3, "white");
	togglePiece(4, 4, "white");

	// Set the black pieces
	togglePiece(3, 4, "black");
	togglePiece(4, 3, "black");
	console.log("Reached the end of setUpReversi()");
}

// MAIN FUNCTION
// - for adding click handlers to each boardspot
function activateBoardSpots() {
	console.log("Activate boardspots!");
	$(".boardspot").on("click", ajax_spotClicked);
}

// AJAX FUNCTION
// - called whenever a boardspot is clicked
function ajax_spotClicked() {
	console.log("Reached the start of ajax_spotClicked()");
	$game_id = $("#game_id").text();
	$currentClass = $(this).attr("class");

	var xy_coords = getXY($(this));

	var mydata = { game_id: $game_id, x: xy_coords.x, y: xy_coords.y };
	// var request = $.post(url_for('make_move'), mydata)
	var request = $.post('reversiapp.py/_make_move', mydata)
	.done(ajax_spotClicked_cb(data))
	.fail(function() { alert("Error"); });

	console.log("Reached the end of ajax_spotClicked()");
}

function ajax_spotClicked_cb(data) {
	console.log("Reached the start of ajax_spotClicked_cb()");
	alert(data);
	console.log("Reached the end of ajax_spotClicked_cb()");
}

// HELPER FUNCTION
// - for toggling boardspots to black or white
function togglePiece($x, $y, $blackorwhite) {
	console.log("togglePiece(): Begin toggling");
	$boardspot = $(".X_"+$x+".Y_"+$y);

	if ($blackorwhite == "white") {
		$boardspot.toggleClass("white", true);
		$boardspot.toggleClass("black", false); 
		$boardspot.toggleClass("empty", false);
		console.log("("+$x+", "+$y+") is now white");
	} else if ($blackorwhite == "black") {
		$boardspot.toggleClass("black", true);
		$boardspot.toggleClass("white", false);
		$boardspot.toggleClass("empty", false);
		console.log("("+$x+", "+$y+") is now black");
	} else if ($blackorwhite == "empty") {
		$boardspot.toggleClass("empty", true);
		$boardspot.toggleClass("white", false);
		$boardspot.toggleClass("black", false);
	}
}

// HELPER FUNCTION
// - for retrieving the x and y coordinates of a boardspot
// Returns JSON with .x and .y fields
function getXY($jquery) {
	$currentClass = $jquery.attr("class");

	// Patterns
	$x_pattern = /X_[0-9]/;
	$y_pattern = /Y_[0-9]/;

	// Class Matches
	var x_match = $currentClass.match($x_pattern);
	var y_match = $currentClass.match($y_pattern);

	// Retrieve Integer values off of X_ and Y_ classes
	$x_match = x_match[0].replace("X_", "");
	$y_match = y_match[0].replace("Y_", "");

	return {"x": $x_match, "y": $y_match};
}