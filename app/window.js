import * as br from "./blindreader.js"

let $ = function(selector) { return document.querySelector(selector) }
var expression
var top_expression

$('#submit').onclick = function(e) {
	let latexInput = '$' + $('#latexInput').value + '$'
	let tokens = br.tokenize(latexInput)
	expression = br.order(tokens)
	top_expression = expression
	let msg = new SpeechSynthesisUtterance(expression.spoken())
	console.log(msg.text)
	window.speechSynthesis.speak(msg)
}

document.onkeydown = function(event) {
	let key_code = event.keyCode
	window.speechSynthesis.cancel()
	let msg
	if (expression) {
		switch(key_code) {
			case 37: // Left
				if (expression.left) {
					expression = expression.left
					msg = new SpeechSynthesisUtterance(expression.spoken())
				}
				break
			case 38: // Up
				if (expression.up) {
					expression = expression.up
					msg = new SpeechSynthesisUtterance(expression.spoken())
				}
				break
			case 39: // Right
				if (expression.right) {
					expression = expression.right
					msg = new SpeechSynthesisUtterance(expression.spoken())
				}
				break
			case 40: // Down
				if (expression.down) {
					expression = expression.down
					msg = new SpeechSynthesisUtterance(expression.spoken())
				}
				break
			case 50: // Read under term
				msg = new SpeechSynthesisUtterance(expression.read_expression())
				break
			case 49: // Read whole expression
				msg = new SpeechSynthesisUtterance(top_expression.read_expression())
				break
		}
		if (msg) {
			console.log(msg.text)
			window.speechSynthesis.speak(msg)
		}
	}
}