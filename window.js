import * as br from "./blindreader.js"

let $ = function(selector) { return document.querySelector(selector) }
var expression
var top_expression
var rate

$('#speak').onclick = function(e) {
	try {
		let latex_render = katex.renderToString($('#latexInput').value)
		document.getElementById("latexDisplay").innerHTML = latex_render
		let latexInput = '$' + $('#latexInput').value + '$'
		let tokens = br.tokenize(latexInput)
		expression = br.order(tokens)
		top_expression = expression
		speakmsg(expression.spoken())
		document.getElementById("#speak").blur()
	}
	catch (err) {
		let error = "Error parsing LaTeX equation, check syntax"
		document.getElementById("latexDisplay").innerHTML = error
		speakmsg(error)
	}
}

$('#rate').onclick = function(e) {
	rate = $('#speakingRate').value
	document.getElementById("#rate").blur()
}

document.onkeydown = function(event) {
	let key_code = event.keyCode
	let msg
	if (expression) {
		switch(key_code) {
			case 37: // Left
				if (expression.left) {
					expression = expression.left
					msg = expression.spoken()
				}
				break
			case 38: // Up
				if (expression.up) {
					expression = expression.up
					msg = expression.spoken()
				}
				break
			case 39: // Right
				if (expression.right) {
					expression = expression.right
					msg = expression.spoken()
				}
				break
			case 40: // Down
				if (expression.down) {
					expression = expression.down
					msg = expression.spoken()
				}
				break
			case 50: // Read under term
				msg = expression.read_expression(false)
				break
			case 49: // Read whole expression
				msg = top_expression.read_expression(false)
				break
		}
		if (msg)
			speakmsg(msg)
	}
}

function speakmsg(message) {
	console.log(message)
	let msg = new SpeechSynthesisUtterance(message)
	if (rate)
		msg.rate = rate
	window.speechSynthesis.cancel()
	window.speechSynthesis.speak(msg)
}