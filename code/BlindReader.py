import symbols
import curses
import os
import multiprocessing as mp
import pyttsx3
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvas
from tkinter import *
from tkinter.ttk import *

def tokenize(text):
	'''
	Tokenizer function which deletes whitespace and separates all important tokens
	for any mathematical expressions in the LaTeX document
	
		Inputs: text is the entire LaTeX document in plaintext
		Returns: an list of all relevent tokens of each math expression found
	'''
	i = 1
	while i < len(text):
		new_expression = ['(']
		while text[i] != '$':
			if text[i] == '=':
				new_expression += [')'] + [text[i]] + ['(']
			elif text[i] == '{':
				new_expression += '('
			elif text[i] == '}':
				new_expression += ')'
			elif text[i] == '\\':
				for key in symbols.all_tex_keys:
					if text[i:i+len(key)] == key:
						new_expression += [symbols.all_tex_keys[key]]
						i += len(key) - 1 
						break
			elif text[i] in symbols.all_tex_keys:
				new_expression += [symbols.all_tex_keys[text[i]]]
			elif text[i] not in '\n ':
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
		return new_expression

def fix_terms(term):
	if term.down:
		fix_terms(term.down)
	if type(term) in symbols.object_fixes:
		term.fix()
	if term.right:
		fix_terms(term.right)

def order(tokens, checked):
	'''
	Function which first parses the math tokens and creates nested 
	lists for any parenthetical terms/function arguments and rearranges
	function arguments then creates linked term objects
	
		Inputs: Math expression token list from tokenize function
		Returns: A linked equation_list object
	'''
	expression = []
	index = 0
	while index < len(tokens):
		inner_expression, index = parse(tokens, index)
		if inner_expression is not None:
			expression += [inner_expression]
	print(expression, "after parse\r")
	expression = terminize(checked, expression, ())
	print(expression, "after expressions")
	# fix_terms(expression)
	return expression


	# expressions = []
	# for token in tokens:
	# 	expression = []
	# 	index = 0
	# 	while index < len(token):
	# 		inner_expression, index = parse(token, index)
	# 		if inner_expression is not None:
	# 			expression += [inner_expression]
	# 	expressions += [expression]
	# print(expressions, "after parse\r")
	# expressions = terminize(checked, expressions, ())
	# print(expressions, "after expressions")
	# fix_terms(expressions)
	# return expressions

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
		if loc in checked: # Returns the next valid right term
			return terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
		else:
			checked.add(loc)

		expression = expressions # Finds the expressions
		i = 0
		while i < len(loc) - 1:
			expression = expression[loc[i]]
			i += 1

		targets = [None, None, None, None]

		if len(loc) == 0: # Determines expression or equation
			targets[1] = terminize(checked, expressions, loc + (0,))
			if len(expression) == 1:
				targets[1] = targets[1].down
				res = symbols.expression(targets)
			else:
				res = symbols.equation(targets)
		elif type(expression[loc[-1]]) == list:
			targets[1] = terminize(checked, expressions, loc + (0,))
			if not arg: # Assigns the right term
				targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
			if arg and len(expression[loc[-1]]) == 1: # Checks for term arguments
				res = symbols.term(targets, expression[loc[-1]][0])
			elif len(loc) == 1:
				res = symbols.expression(targets, loc[0]//2 + 1)
			else:
				res = symbols.parenthetical(targets)
		elif expression[loc[-1]] in symbols.tex_args:
			func, arg = symbols.tex_args[expression[loc[-1]]]
			args = expression[loc[-1]+1:loc[-1]+1+arg]
			for i in range(arg):
				args[i] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+i,), True)
			targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+arg,))
			res = func(targets, args)
		else:
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






	try:
		if loc in checked:
			return terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
		else:
			checked.add(loc)
		expression = expressions
		i = 0
		while i < len(loc) - 1:
			expression = expression[loc[i]]
			i += 1

		targets = [None, None, None, None]

		if len(loc) == 0:
			targets[1] = terminize(checked, expressions, loc + (0,))
			res = symbols.equation_list(targets, len(expression))
		elif type(expression[loc[-1]]) == list:
			targets[1] = terminize(checked, expressions, loc + (0,))
			if not arg and len(loc) > 0:
				targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1,))
			if arg and len(expression[loc[-1]]) == 1:
				res = symbols.term(targets, expression[loc[-1]][0])
			elif len(loc) == 1: 
				if len(expression[loc[-1]]) == 1:
					targets[1] = targets[1].down.down
					res = symbols.expression(targets)
				else:
					res = symbols.equation(targets)
			elif len(loc) == 2:
				res = symbols.expression(targets, loc[-1]//2 + 1)
			res = symbols.parenthetical(targets)
		elif expression[loc[-1]] in symbols.tex_args:
			func, arg = symbols.tex_args[expression[loc[-1]]]
			args = expression[loc[-1]+1:loc[-1]+1+arg]
			for i in range(arg):
				args[i] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+i,), True)
			targets[3] = terminize(checked, expressions, loc[:len(loc)-1] + (loc[-1]+1+arg,))
			res = func(targets, args)
		else:
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

def poller(output_queue, new_queue):
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
	expression = new_queue.get()

	while True:
		if not new_queue.empty():
			expression = new_queue.get()
		char = stdscr.getch()
		if expression is not None:
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

			if char != -1 and char != curses.KEY_ENTER:
				statement = expression.spoken()
				output_queue.put(statement)

def reader(output_queue):
	voices_i = [0, 7, 36]
	speaker_process = mp.Process(target = speaker, args = ('',))
	while True:
		statement = output_queue.get()
		print(statement, '\r')
		if speaker_process.is_alive():
			speaker_process.terminate()
		speaker_process = mp.Process(target = speaker, args = (statement,))
		speaker_process.start()

def speaker(statement, v = 0): 
	'''
	Text to speech function which initializes the tts engine then process 
	the statement to be read. This function is to be terminated when a new
	keyboard input is detected

		Inputs: statement is the current statement to be read out
				v is the current voice to read out the statement
	'''
	engine = pyttsx3.init()
	voices = engine.getProperty('voices')
	process_statement(engine, statement, voices, v)
	engine.runAndWait()

def process_statement(engine, statement, voices, v):
	'''
	Function which process the statements put on the global statement 
	queue. Adjusts the tts engine's voice according to parenthetical 
	terms. 

		Inputs:	engine is the tts engine (pyttsx3 module)
				statement is the statement to be read aloud
				voices is the list of voices available from the engine
				v is the current index that selects the engine's voice
	'''
	current_v = v
	if v == len(voices_i) - 1:
		next_v = 0
	else:
		next_v = v + 1
	s = 0
	while s < len(statement):
		if statement[s] == "parenthetical":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(engine, statement[s+1], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			v = current_v
			s += 2
		elif statement[s] == "frac1":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(engine, statement[s+1], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			engine.say(statement[s+2])
			s += 3
		elif statement[s] == "frac2":
			engine.say(statement[s+1])
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			process_statement(engine, statement[s+2], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			s += 3
		else:
			output = ''
			while s != len(statement) and statement[s] != "parenthetical":
				output += statement[s]
				s += 1
			engine.say(output)

def graph(text):
	tmptext = entry.get()
	tmptext, new_expression = "$"+tmptext+"$", "$"+tmptext+"$"
	loc = []
	statement = []
	parsed = tokenize(new_expression)
	print(parsed, "after tokenize")
	expression = order(parsed, set())
	print(expression)
	new_queue.put(expression)

	ax.clear()
	ax.text(0.2, 0.6, tmptext, fontsize = 50)  
	canvas.draw()

if __name__ == '__main__':

	new_queue = mp.Queue()
	output_queue = mp.Queue()

	keyboard_process = mp.Process(target = poller, args = (output_queue, new_queue))
	reader_process = mp.Process(target = reader, args = (output_queue,))
	keyboard_process.start()
	reader_process.start()

	root = Tk()
	mainframe = Frame(root)
	mainframe.pack()

	text = StringVar()
	entry = Entry(mainframe, width=110, textvariable=text)
	entry.pack()

	label = Label(mainframe)
	label.pack()

	fig = matplotlib.figure.Figure(figsize=(6, 6), dpi=100)
	ax = fig.add_subplot(111)

	canvas = FigureCanvas(fig, master=label)
	canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
	canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)

	root.bind('<Return>', graph)
	root.mainloop()









	# while True:
	# 	expression = expression_queue.get()
	# 	if reader_process.is_alive():
	# 		reader_process.terminate()
	# 	reader_process = mp.Process(target = reader, args = (expression, output_queue))
	# 	reader_process.start()

	# expression = expression_queue.get()
	# queue = multiprocessing.Queue()
	# statement = ''
	# loc = []
	# statement = []
	# voices_i = [0, 7, 36]
	# tokens = tokenize(expression)
	# expression = order(tokens)
	# keyboard_process = multiprocessing.Process(target = poller, args = (queue, expression))
	# speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
	# keyboard_process.start()

	# root = Tk()
	# main = ttk.Frame(root)
	# root.mainloop()

	# while True:
	# 	v = 0
	# 	statement = queue.get()
	# 	print(statement, '\r')
	# 	if speaker_process.is_alive():
	# 		speaker_process.terminate()
	# 	speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
	# 	speaker_process.start()




######################################################

	# File = open('test_latex.tex', 'r').read()
	# queue = multiprocessing.Queue()
	# statement = ''
	# loc = []
	# statement = []
	# checked = set()
	# voices_i = [0, 7, 36]
	# tokens = tokenize(File)
	# print(tokens, "after tokenize", '\r')
	# ordered = order(tokens)
	# print(ordered, "after terminize", '\r')
	# expression = ordered
	# keyboard_process = multiprocessing.Process(target = poller, args = (queue, expression))
	# speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
	# keyboard_process.start()

	# root = Tk()
	# main = ttk.Frame(root)
	# root.mainloop()

	# while True:
	# 	v = 0
	# 	statement = queue.get()
	# 	print(statement, '\r')
	# 	if speaker_process.is_alive():
	# 		speaker_process.terminate()
	# 	speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
	# 	speaker_process.start()