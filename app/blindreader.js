import symbols

function tokenize(text) {
	/*
	Tokenizer function which deletes whitespace and separates all important tokens
	for any mathematical expressions in the LaTeX document
	
		Inputs: text is the entire LaTeX document in plaintext
		Returns: an list of all relevent tokens of each math expression found
	*/
	let i = 0 // Index
	let tokens = [] // An array of all expressions

	while (i < text.length) {
		if (text[i] == '$' || text.substr(i,2) == '\\[') { // Start sequence for LaTeX math mode
			if (text[i] == '$')
				i += 1
			else if (text.substr(i,2) == '\\[')
				i += 2
			let new_expression = ['(']
			while (text[i] != '$' && text.substr(i,2) != '\\[') { // End sequence for LaTeX math mode
				if (text[i] == '=')
					new_expression = new_expression.concat([')'], [text[i]], ['('])
				else if (text[i] == '{')
					new_expression.push('(')
				else if (text[i] == '}')
					new_expression.push(')')
				else if (text[i] == '\\') { // Escape sequence for most LaTeX special characters
					for (let key of symbols.all_tex_keys) {
						if (text.substr(i, key.length) == key) {
							new_expression.push(symbols.all_tex_keys[key])
							i += key.length - 1 
							break
						}
					}
				}
				else if (text[i] in symbols.all_tex_keys)
					new_expression.push(symbols.all_tex_keys[text[i]])
				else if (!'\n '.includes(text[i])) { // Catching all valid numbers
					let term = text[i]
					if (term in symbols.numbers) {
						i += 1
						while (text[i] in symbols.numbers) {
							term[0] += text[i]
							i += 1
						}
						i -= 1
					}
					new_expression.push(term)
				}
				i += 1
			}
			new_expression.push(')')
			tokens.push(new_expression)
		}
		i += 1
	}
	return tokens
}

function order(tokens, checked) {
	/*
	Function which first parses the math tokens and creates nested 
	lists for any parenthetical terms/function arguments and rearranges
	function arguments then creates linked term objects
	
		Inputs: Math expression token list from tokenize function
		Returns: A linked equation_list object
	*/
	let expressions = [] // The list of all expressions
	for (let token of tokens) {
		let expression = []
		let index = 0
		while (index < token.length) {
			let parse_res = parse(token, index)
			let inner_expression = parse_res[0]
			let index = parse_res[1]
			if (!(inner_expression == null)):
				expression.push(inner_expression)
		}
		expressions.push(expression)
	}
	console.log(expressions, "after parse")
	let expression = terminize(checked, expressions, ())
	console.log(expression, "after terminize")
	return fix_terms(expression)
}

function parse(token, index) {
	/*
	Parsing function which rearranges tokens and creates nested lists 
	of parenthetical terms

		Inputs: Token list to be parsed
		Returns: The new, parsed token/token list and the next index
	*/
	while (index < token.length) {
		if (token[index] == '(') {
			let expression = []
			let parse_res = parse(token, index + 1)
			let inner_expression = parse_res[0]
			let index = parse_res[1]
			while (!(inner_expression == null)) {
				expression.push(inner_expression)
				parse_res = parse(token, index)
				inner_expression = parse_res[0]
				index = parse_res[1]
			}
			return [expression, index]
		}
		else if (token[index] == ')')
			return [null, index + 1]
		else if (token[index] == '=')
			return ['=', index + 1]
		else
			return [token[index], index + 1]
	}
}

function terminize(checked, expressions, loc, arg = false) {
	/*
	Terminizer function which navigates the entire expression list and initialize
	linked term objects according to their type

		Inputs: checked is the set of all locations which have already been
					previously ran through this function
				expressions is the entire mathematical expression list after 
					being passed through tokenize and parse functions
				loc is the current location within the expression list, this
					is the token to be evaluated/initialized
				arg is an optional argument which indicates if the current
					token at loc is an argument to a previous term
		Returns: a linked term object
	*/
	if (checked.has(JSON.stringify(loc))) // Prevents double-use of LaTeX object arguments
		return terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[-1]+1))
	else
		checked.add(JSON.stringify(loc))

	let expression = expressions
	let i = 0
	while (i < loc.length - 1) {
		expression = expression[loc[i]]
		if (expression == undefined)
			return null
		i += 1
	}
	if (loc.length > 0 && expression[loc[-1]] == undefined)
		return null

	targets = [null, null, null, null]

	if (loc.length == 0) { //  default is always an equation list
		targets[1] = terminize(checked, expressions, loc.concat([0]))
		let res = symbols.equation_list(targets, expression.length)
	}
	else if (Array.isArray(expression[loc[-1]])) {
		targets[1] = terminize(checked, expressions, loc.concat([0]))
		if (!arg) // Arguments do not have right expressions
			targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[-1]+1))
		if (arg && expression[loc[-1]].length == 1) // Single listed arguments are treated as terms
			let res = symbols.term(targets, expression[loc[-1]][0])
		else if (loc.length == 1) { // Expression/Equation differentiation
			if (expression[loc[-1]].length == 1) {
				targets[1] = targets[1].down
				let res = symbols.expression(targets)
			}
			else
				let res = symbols.equation(targets)
		}
		else if (loc.length == 2 && expression.includes("=")) // Numbered expressions within equations
			let res = symbols.expression(targets, Math.floor(loc[-1]/2)+1)
		else // Parentheticals
			let res = symbols.parenthetical(targets)
	}
	else if (expression[loc[-1]] in symbols.tex_args) { // LaTeX specific keywords
		let res = symbols.tex_args[expression[loc[-1]]] // Function and number of arguments
		let func = res[0]
		let arg = res[1]
		let args = expression.slice(loc[-1]+1, loc[-1]+1+arg)
		for (i = 0; i < arg; i ++)
			args[i] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[-1]+1+i), true) // Terminize all arguments
		targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[-1]+1+arg)) // Get the right expression
		let res = func(targets, args)
	}
	else { // All other terms
		if (!arg)
			targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[-1] + 1))
		let res = symbols.term(targets, expression[loc[-1]])
	}

	let term = res.down
	while (term != null) {
		term.up = res
		term = term.right
	}
	if (res.right)
		res.right.left = res

	return res
}

function fix_terms(term) {
	/*
	Helper function which naviates the passed in term object and
	fixes their targets by calling their respective fix methods.
	This is necessary after parsing the LaTeX input because some 
	LaTeX objects, like '^' have an attribute that comes before 
	'^', whereas others, like '\frac{}{}', don't need fixing
	because the object's attributes are all in front, so they are
	accounted for in the terminize function

		Inputs: term is the linked term object to be navigated
	*/
	if (term.down)
		fix_terms(term.down)
	if (typeof term.fix == "function")
		term.fix()
	if (term.right)
		fix_terms(term.right)
}

// function poller(output_queue, expression):
// 	/*
// 	Keyboard polling function, ran on a separate process which 
// 	waits for a keyboard input and then processes it accordingly,
// 	adding to the global queue the next statement to be read out

// 		Inputs: queue is the global statement queue
// 				expression is the linked expression object to be navigated
// 	*/
// 	stdscr = curses.initscr()
// 	stdscr.keypad(true)
// 	stdscr.timeout(-1)
// 	top_expression = null
// 	statement = ''
// 	valid_chars = {10, 49, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN}
// 	flag = true

// 	while true:
// 		char = stdscr.getch()
// 		if expression is !null:
// 			if char == 10:
// 				statement = get_statement(expression.read_expression(false))
// 				flag = true
// 			else if char == 49:
// 				if top_expression:
// 					statement = get_statement(top_expression.read_expression(false))
// 					flag = true
// 				else:
// 					flag = false
// 			else:
// 				if char == curses.KEY_LEFT:
// 					if expression.left:
// 						expression = expression.left
// 						flag = true
// 					else:
// 						flag = false
// 				else if char == curses.KEY_RIGHT:
// 					if expression.right:
// 						expression = expression.right
// 						flag = true
// 					else:
// 						flag = false
// 				else if char == curses.KEY_UP:
// 					if expression.up:
// 						expression = expression.up
// 						flag = true
// 					else:
// 						flag = false
// 				else if char == curses.KEY_DOWN:
// 					if expression.down:
// 						expression = expression.down
// 						flag = true
// 					else:
// 						flag = false
// 				if type(expression) == symbols.equation || (type(expression) == symbols.expression && !expression.num):
// 					top_expression = expression
// 				else if type(expression) == symbols.equation_list:
// 					top_expression = null
// 				statement = get_statement(expression.spoken())

// 			if char in valid_chars && flag:
// 				output_queue.put(statement)
// 				console.log(statement, '\r')

// function speaker(statement): 
// 	/*
// 	Text to speech function which initializes the tts engine then process 
// 	the statement to be read. This function is to be terminated when a new
// 	keyboard input is detected

// 		Inputs: statement is the current statement to be read out
// 				v is the current voice to read out the statement
// 	*/
// 	engine = pyttsx3.init()
// 	engine.say(statement)
// 	engine.runAndWait()

// function get_statement(statement):
// 	/*
// 	I made this helper function because I fucked this up when 
// 	coding for the pyttsx3 engine to change voices. This 
// 	function takes in the passed in statement nested list 
// 	and returns the string representation of the statement. 
// 	Please change this if you can. You'll have to go into 
// 	symbols.py and change all the list outputs for 
// 	spoken/read_expression to string outputs.

// 		Inputs: statement list object
// 		Returns: string version of the statement
// 	*/
// 	res = ''
// 	s = 0
// 	while s < len(statement):
// 		if statement[s] == "parenthetical":
// 			res += get_statement(statement[s+1])
// 			s += 2
// 		else:
// 			res += statement[s]
// 			s += 1
// 	return res

// if __name__ == '__main__':

// 	// Process the desired LaTeX document, and open it
// 	os.system("test_latex.tex")
// 	os.system("open test_latex.pdf")
// 	text = open('test_latex.tex', 'r').read()

// 	// Used for parsing/processing the LaTeX file
// 	loc = []
// 	statement = []
// 	checked = set()

// 	// Process the LaTeX file
// 	parsed = tokenize(text)
// 	console.log(parsed, "after tokenize", '\r')
// 	ordered = order(parsed, checked)
// 	expression = ordered

// 	// queue is the output queue which the keyboard polling 
// 	// process puts every new statement to be read out by
// 	// the speaker_process
// 	queue = mp.Queue()
// 	keyboard_process = mp.Process(target = poller, args = (queue, expression))
// 	speaker_process = mp.Process(target = speaker, args = (statement,))
// 	keyboard_process.start()

// 	// Forever while loop which continually checks for new 
// 	// outputs in the queue, then stops the current speaker
// 	// process if it is running, and starts a new one
// 	while true:
// 		statement = queue.get()
// 		if speaker_process.is_alive():
// 			speaker_process.terminate()
// 		speaker_process = mp.Process(target = speaker, args = (statement,))
//		speaker_process.start()