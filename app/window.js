import * as br from "./blindreader.js"

let $ = function(selector) { return document.querySelector(selector); }
let expression

$('#submit').onclick = function(e) {
	let latexInput = '$' + $('#latexInput').value + '$'
	let tokens = br.tokenize(latexInput)
	expression = br.order(tokens)
	console.log(typeof expression)
	console.log(expression.read_expression())
}

document.onkeydown = function(event) {
	var key_code = event.keyCode;
	if (expression) {
		switch(key_code) {
			case 37: // Left
				if (expression.left)
					expression = expression.left
				break
			case 38: // Up
				if (expression.up)
					expression = expression.up
				break
			case 39: // Right
				if (expression.right)
					expression = expression.right
				break
			case 40: // Down
				if (expression.down)
					expression = expression.down
				break
			case 149: // Read under term
				if (expression.left)
					expression = expression.left
				break
			case 250: // Read whole expression
				if (expression.right)
					expression = expression.right
				break
		}
		console.log(expression.spoken())
	}
}