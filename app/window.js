import * as br from "blindreader"

$ = function(selector) { return document.querySelector(selector); }

$('#submit').onclick = function(e) {
	var latexInput = $('#latexInput')
	console.log(latexInput)
};