import symbols, os, multiprocessing, pyttsx3

def tokenize(text):
	'''
	Tokenizer function to isolate individual expressions and delete white space
	'''
	i = 0
	tokens = []

	while i < len(text):
		if text[i] == '$' or text[i:i+2] == '\\[':
			if text[i] == '$':
				i += 1
			elif text[i:i+2] == '\\[':
				i += 2
			new_expression = ['(']
			while text[i] != '$' and text[i:i+2] != '\\]':
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
				elif text[i] == '^':
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
			tokens += [new_expression]
		i += 1
	return tokens

def parse(token, index):
	while index < len(token):
		if token[index] == '(':
			expression = []
			inner_expression, index = parse(token, index + 1)
			while inner_expression is not None:
				expression += [inner_expression]
				if inner_expression == 'pow':
					expression[-2], expression[-1] = expression[-1], expression[-2]
				inner_expression, index = parse(token, index)
			return expression, index
		elif token[index] == ')':
			return None, index + 1
		elif token[index] == '=':
			return '=', index + 1
		else:
			return token[index], index + 1

def group(expression):
	new_expression = []
	checked = set()
	for i in range(len(expression)):
		if i not in checked:
			if type(expression[i]) != list:
				new_term = expression[i]
				if expression[i].lower() in symbols.numbers + symbols.letters:
					checked.add(i) 
					for j in range(i + 1, len(expression)):
						if type(expression[j]) != list and expression[j].lower() in symbols.numbers + symbols.letters:
							checked.add(j)
							new_term += expression[j]
						else:
							break
			else:
				new_term = group(expression[i])
			new_expression += [new_term]
	return new_expression

def terminize(expressions, loc, arg = False):
	try:
		if loc in checked:
			return terminize(expressions, loc[:len(loc)-1] + (loc[-1]+1,))
		else:
			checked.add(loc)
		expression = expressions
		i = 0
		while i < len(loc) - 1:
			expression = expression[loc[i]]
			i += 1

		targets = [None, None, None, None]

		if len(loc) == 0:
			targets[1] = terminize(expressions, loc + (0,))
			res = symbols.equation_list(targets, len(expression))
		elif type(expression[loc[-1]]) == list:
			targets[1] = terminize(expressions, loc + (0,))
			if not arg and len(loc) > 0:
				targets[3] = terminize(expressions, loc[:len(loc)-1] + (loc[-1]+1,))
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
			else:
				res = symbols.parenthetical(targets)
		elif expression[loc[-1]] in symbols.tex_args:
			func, arg = symbols.tex_args[expression[loc[-1]]]
			args = expression[loc[-1]+1:loc[-1]+1+arg]
			for i in range(arg):
				args[i] = terminize(expressions, loc[:len(loc)-1] + (loc[-1]+1+i,), True)
			targets[3] = terminize(expressions, loc[:len(loc)-1] + (loc[-1]+1+arg,))
			res = func(targets, args)
		else:
			if not arg:
				targets[3] = terminize(expressions, loc[:len(loc)-1] + (loc[-1]+1,))
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

def order(tokens):
	expressions = []

	for token in tokens:
		expression = []
		index = 0
		while index < len(token):
			inner_expression, index = parse(token, index)
			if inner_expression is not None:
				expression += [inner_expression]
		expressions += [expression]

	print(expressions, "after parse\r")

	return terminize(expressions, ())

def process_input(expressions, loc, inp):
	expression = expressions

	for i in loc[:-1]:
		expression = expression[i]
	if inp == "UP":
		if len(loc) > 0:
			loc.pop()
	elif inp == "DOWN":
		if (len(loc) == 0 and type(expression[0]) == list) or type(expression[loc[-1]]) == list:
			loc += [0] 
	elif inp == "LEFT":
		if type(expression) == list and len(loc) > 0 and loc[-1] > 0:
			loc[-1] = loc[-1] - 1
	elif inp == "RIGHT":
		if type(expression) == list and len(loc) > 0 and loc[-1] < len(expression) - 1:
			loc[-1] = loc[-1] + 1
	
	expression = expressions

	for i in loc:
		expression = expression[i]
	return expression

def interpreter(expression, loc):
	statement = ''
	if len(loc) == 0:
		statement = "This is a list of " + str(len(expression)) + " equation" + ('s' if len(expression) > 1 else '')
	elif len(loc) == 1:
		if len(expression) == 1:
			statement = "This is an expression with " + str(len(expression[0])) + " term" + ('s' if len(expression[0]) > 1 else '')
		else:
			statement = 'This is an equation. '
			j = 1
			for i in range(len(expression)):
				if type(expression[i]) == list:
					statement += 'expression ' + str(j) + ' '
					j += 1
				elif expression[i] == '=':
					statement += 'equals '
	else:
		if type(expression) == list:
			if len(loc) > 2:
				statement = "Parenthetical term. "
			for i in range(len(expression)):
				if type(expression[i]) == list:
					statement += "a term "
				elif expression[i] == '/':
					statement += "divided by "
				elif expression[i] == '+':
					statement += "plus "
				elif expression[i] == '-':
					statement += "minus "
				else:
					statement += expression[i] + '. '
				if i < len(expression) - 1 and (type(expression[i]) == list or expression[i] in symbols.numbers + symbols.letters) and (type(expression[i+1]) == list or expression[i+1] in symbols.numbers + symbols.letters):
					statement += "times "
		else:
			if type(expression) == str:
				if expression == '/':
					statement = "divided by "
				elif expression == '+':
					statement = "plus "
				elif expression == '-':
					statement = "minus "
				else:
					statement = expression + ". "
	if len(statement) == 0:
		statement = "ERROR"
	print(statement, '\r')
	return statement

def poller(queue, expression):
	import curses
	stdscr = curses.initscr()
	stdscr.keypad(True)
	stdscr.timeout(-1)

	while True:
		char = stdscr.getch()
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

		if char != -1:
			statement = expression.spoken()
			queue.put(statement)

def speaker(statement, v = 0): 
	engine = pyttsx3.init()
	voices = engine.getProperty('voices')
	pitch(engine, statement, voices, v)
	engine.runAndWait()

def pitch(engine, statement, voices, v):
	current_v = v
	if v == len(voices_i) - 1:
		next_v = 0
	else:
		next_v = v + 1
	s = 0
	while s < len(statement):
		if statement[s] == "parenthetical":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			pitch(engine, statement[s+1], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			v = current_v
			s += 2
		elif statement[s] == "frac1":
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			pitch(engine, statement[s+1], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			engine.say(statement[s+2])
			s += 3
		elif statement[s] == "frac2":
			engine.say(statement[s+1])
			engine.setProperty('voice', voices[voices_i[next_v]].id)
			pitch(engine, statement[s+2], voices, next_v)
			engine.setProperty('voice', voices[voices_i[current_v]].id)
			s += 3
		else:
			output = ''
			while s != len(statement) and statement[s] != "parenthetical":
				output += statement[s]
				s += 1
			engine.say(output)

if __name__ == '__main__':
	File = open('test_latex.tex', 'r').read()
	queue = multiprocessing.Queue()
	statement = ''
	loc = []
	statement = []
	checked = set()
	voices_i = [0, 7, 36]
	parsed = tokenize(File)
	print(parsed, "after tokenize", '\r')
	ordered = order(parsed)
	print(ordered, "after terminize", '\r')
	expression = ordered
	keyboard_process = multiprocessing.Process(target = poller, args = (queue, expression))
	speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
	keyboard_process.start()

	while True:
		v = 0
		statement = queue.get()
		print(statement, '\r')
		if speaker_process.is_alive():
			speaker_process.terminate()
		speaker_process = multiprocessing.Process(target = speaker, args = (statement,))
		speaker_process.start()