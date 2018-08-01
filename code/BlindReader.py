import symbols
import curses
import os
import multiprocessing as mp
import pyttsx3
import subprocess

def tokenize(text):
	'''
	Tokenizer function which deletes whitespace and separates all important tokens
	for any mathematical expressions in the LaTeX document
	
		Inputs: text is the entire LaTeX document in plaintext
		Returns: an list of all relevent tokens of each math expression found
	'''
	i = 0 # Index
	tokens = [] # A list of all expressions

	while i < len(text):
		if text[i] == '$' or text[i:i+2] == '\\[': # Start sequence for LaTeX math mode
			if text[i] == '$':
				i += 1
			elif text[i:i+2] == '\\[':
				i += 2
			new_expression = ['(']
			while text[i] != '$' and text[i:i+2] != '\\]': # End sequence for LaTeX math mode
				if text[i] == '=':
					new_expression += [')'] + [text[i]] + ['(']
				elif text[i] == '{':
					new_expression += '('
				elif text[i] == '}':
					new_expression += ')'
				elif text[i] == '\\': # Escape sequence for most LaTeX special characters
					for key in symbols.all_tex_keys:
						if text[i:i+len(key)] == key:
							new_expression += [symbols.all_tex_keys[key]]
							i += len(key) - 1 
							break
				elif text[i] in symbols.all_tex_keys:
					new_expression += [symbols.all_tex_keys[text[i]]]
				elif text[i] not in '\n ': # Catching all valid numbers
					term = [text[i]]
					if term[0] in symbols.numbers:
						i += 1
						while text[i] in symbols.numbers:
							term[0] += text[i]
							i += 1
						i -= 1
					new_expression += term
				i += 1
			new_expression += [')']
			tokens += [new_expression]
		i += 1
	return tokens

def order(tokens, checked):
	'''
	Function which first parses the math tokens and creates nested 
	lists for any parenthetical terms/function arguments and rearranges
	function arguments then creates linked term objects
	
		Inputs: Math expression token list from tokenize function
		Returns: A linked equation_list object
	'''
	expressions = [] # The list of all expressions
	for token in tokens:
		expression = []
		index = 0
		while index < len(token):
			inner_expression, index = parse(token, index)
			if inner_expression is not None:
				expression += [inner_expression]
		expressions += [expression]

	print(expressions, "after parse\r")
	expression = terminize(checked, expressions, ())
	print(expression, "after terminize")
	fix_terms(expression)
	return expression

def parse(token, index):
	'''
	Parsing function which rearranges tokens and creates nested lists 
	of parenthetical terms

		Inputs: Token list to be parsed
		Returns: The new, parsed token/token list and the next index
	'''
	while index < len(token):
		if token[index] == '(':
			expression = []
			inner_expression, index = parse(token, index + 1)
			while inner_expression is not None:
				expression += [inner_expression]
				inner_expression, index = parse(token, index)
			return expression, index
		elif token[index] == ')':
			return None, index + 1
		elif token[index] == '=':
			return '=', index + 1
		else:
			return token[index], index + 1

def terminize(checked, expressions, loc, arg = False):
	'''
	Terminizer function which navigates the entire expression list and initialize
	linked term objects according to their type

		Inputs: expressions is the entire mathematical expression list after 
					being passed through tokenize and parse functions
				loc is the current location within the expression list, this
					is the token to be evaluated/initialized
				arg is an optional argument which indicates if the current
					token at loc is an argument to a previous term
		Returns: a linked term object
	'''
	try:
		if loc in checked: # Prevents double-use of LaTeX arguments
			return terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
		else:
			checked.add(loc)

		expression = expressions
		i = 0
		while i < len(loc) - 1:
			expression = expression[loc[i]]
			i += 1

		targets = [None, None, None, None]

		if len(loc) == 0: # Default is always an equation list
			targets[1] = terminize(checked, expressions, loc + (0,))
			res = symbols.equation_list(targets, len(expression))
		elif type(expression[loc[-1]]) == list:
			targets[1] = terminize(checked, expressions, loc + (0,))
			if not arg: # Arguments do not have right expressions
				targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
			if arg and len(expression[loc[-1]]) == 1: # Single listed arguments are treated as terms
				res = symbols.term(targets, expression[loc[-1]][0])
			elif len(loc) == 1: # Expression/Equation differentiation
				if len(expression[loc[-1]]) == 1:
					targets[1] = targets[1].down
					res = symbols.expression(targets)
				else:
					res = symbols.equation(targets)
			elif len(loc) == 2 and "=" in expression: # Numbered expressions within equations
				res = symbols.expression(targets, loc[-1]//2 + 1)
			else: # Parentheticals
				res = symbols.parenthetical(targets)
		elif expression[loc[-1]] in symbols.tex_args: # LaTeX specific keywords
			func, arg = symbols.tex_args[expression[loc[-1]]] # Function and number of arguments
			args = expression[loc[-1]+1:loc[-1]+1+arg]
			for i in range(arg):
				args[i] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+i,), True) # Terminize all arguments
			targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+arg,)) # Get the right expression
			res = func(targets, args)
		else: # All other terms
			if not arg:
				targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
			res = symbols.term(targets, expression[loc[-1]])

		term = res.down
		while term != None:
			term.up = res
			term = term.right
		if res.right:
			res.right.left = res

		return res

	except IndexError:
		return None

def fix_terms(term):
	if term.down:
		fix_terms(term.down)
	if type(term) in symbols.object_fixes:
		term.fix()
	if term.right:
		fix_terms(term.right)

def poller(output_queue, expression):
	'''
	Keyboard polling function, ran on a separate process which 
	waits for a keyboard input and then processes it accordingly,
	adding to the global queue the next statement to be read out

		Inputs: queue is the global statement queue
				expression is the linked expression object to be navigated
	'''
	stdscr = curses.initscr()
	stdscr.keypad(True)
	stdscr.timeout(-1)
	top_expression = None
	statement = []

	while True:
		char = stdscr.getch()
		if expression is not None:
			if char == 10:
				statement = expression.read_expression(False)
			elif char == 49:
				if top_expression:
					statement = top_expression.read_expression(False)
			else:
				if char == curses.KEY_LEFT:
					if expression.left:
						expression = expression.left
				elif char == curses.KEY_RIGHT:
					if expression.right:
						expression = expression.right
				elif char == curses.KEY_UP:
					if expression.up:
						expression = expression.up
				elif char == curses.KEY_DOWN:
					if expression.down:
						expression = expression.down
				if type(expression) == symbols.equation or (type(expression) == symbols.expression and not expression.num):
					top_expression = expression
				elif type(expression) == symbols.equation_list:
					top_expression = None
				statement = expression.spoken()

			output_queue.put(statement)
			print(statement, '\n\r')

def speaker(statement): 
	'''
	Text to speech function which initializes the tts engine then process 
	the statement to be read. This function is to be terminated when a new
	keyboard input is detected

		Inputs: statement is the current statement to be read out
				v is the current voice to read out the statement
	'''
	engine = pyttsx3.init()
	engine.say(get_statement(statement))
	engine.runAndWait()

def get_statement(statement):
	res = ''
	s = 0
	while s < len(statement):
		if statement[s] == "parenthetical":
			res += get_statement(statement[s+1])
			s += 2
		else:
			res += statement[s]
			s += 1
	return res

def process_statement(statement, v, engine, voices):
	'''
	Function which process the statements put on the global statement 
	queue. Adjusts the tts engine's voice according to parenthetical 
	terms. 

		Inputs:	engine is the tts engine (pyttsx3 module)
				statement is the statement to be read aloud
				voices is the list of voices available from the engine
				v is the current index that selects the engine's voice
	'''
	voices_i = [0, 7, 36]
	current_v = v
	if v == len(voices_i) - 1:
		next_v = 0
	else:
		next_v = v + 1
	s = 0
	while s < len(statement):
		if statement[s] == "parenthetical":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(statement[s+1], next_v, engine, voices)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			v = current_v
			s += 2
		elif statement[s] == "frac1":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(statement[s+1], next_v, engine, voices)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			engine.say(statement[s+2])
			s += 3
		elif statement[s] == "frac2":
			engine.say(statement[s+1])
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(statement[s+2], next_v, engine, voices)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			s += 3
		else:
			output = ''
			while s != len(statement) and statement[s] != "parenthetical":
				output += statement[s]
				s += 1
			engine.say(output)

if __name__ == '__main__':
	os.system("latex test_latex.tex")
	os.system("open test_latex.dvi")
	File = open('test_latex.tex', 'r').read()
	loc = []
	statement = []
	checked = set()
	voices_i = [0, 7, 36]
	parsed = tokenize(File)
	print(parsed, "after tokenize", '\r')
	ordered = order(parsed, checked)
	expression = ordered
	queue = mp.Queue()
	keyboard_process = mp.Process(target = poller, args = (queue, expression))
	speaker_process = mp.Process(target = speaker, args = (statement,))
	keyboard_process.start()

	while True:
		v = 0
		statement = queue.get()
		if speaker_process.is_alive():
			speaker_process.terminate()
		speaker_process = mp.Process(target = speaker, args = (statement,))
		speaker_process.start()