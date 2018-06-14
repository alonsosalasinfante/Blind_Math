import symbols, curses, os
File = open('test_latex.tex', 'r').read()
stdscr = curses.initscr()
stdscr.keypad(True)
stdscr.nodelay(True)

def tokenize(text):
	'''
	Tokenizer function to isolate individual expressions and delete white space
	'''
	i = 0
	tokens = []

	while i < len(text):
		if text[i] == '$':
			new_expression = ['(']
			i += 1
			while text[i] != '$':
				if text[i] == '=':
					new_expression += [')'] + [text[i]] + ['(']
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
				inner_expression, index = parse(token, index)
			return expression, index
		elif token[index] == ')' or token[index] == '=':
			return None, index + 1
		else:
			return token[index], index + 1

def term(expression):
	new_expression = []
	checked = set()
	for i in range(len(expression)):
		if i not in checked:
			if type(expression[i]) != list:
				new_term = expression[i]
				if i not in checked and (expression[i].lower() in symbols.numbers + symbols.letters or expression[i] == '/'):
						checked.add(i) 
						for j in range(i + 1, len(expression)):
							if type(expression[j]) != list and (expression[j].lower() in symbols.numbers + symbols.letters or expression[j] == '/'):
								checked.add(j)
								new_term += expression[j]
							else:
								break
			else:
				new_term = term(expression[i])
			new_expression += [new_term]
	return new_expression

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

	new_expressions = []

	for expression in expressions:
		new_expression = []
		for e in expression:
			new_expression += [term(e)]
		new_expressions += [new_expression]

	return new_expressions

def process_input(expressions, location, inp):
	expression = expressions
	for i in location[:-1]:
		expression = expression[i]
	if inp == "UP":
		if len(location) > 0:
			location.pop()
	elif inp == "DOWN":
		if (len(location) == 0 and type(expression[0]) == list) or type(expression[location[-1]]) == list:
			location += [0] 
	elif inp == "LEFT":
		if type(expression) == list and len(location) > 0 and location[-1] > 0:
			location[-1] = location[-1] - 1
	elif inp == "RIGHT":
		if type(expression) == list and len(location) > 0 and location[-1] < len(expression) - 1:
			location[-1] = location[-1] + 1
	expression = expressions
	for i in location:
		expression = expression[i]
	print(expression.__repr__())
	return expression

def to_speech(expression, location):
	statement = ''
	print("$$$$$$$$$$$", expression)
	if len(location) == 0:
		statement = "A list of " + str(len(expression)) + " equations"
	elif len(location) == 1:
		if len(expression) == 1:
			statement = "An expression with " + str(len(expression[0])) + " terms"
		else:
			statement = "An equation with " + str(len(expression)) + " expressions"
	else:
		if type(expression) == list:
			statement = "An expression with " + str(len(expression)) + " terms"
		else:
			if type(expression) == str:
				if expression[-1] == '/' and len(expression) > 1:
					statement = expression[:-1] + " divided by a term"
				elif expression[0] == '/' and len(expression) > 1:
					statement = "divided by " + expression[1:]
				elif expression == '/':
					statement = "divided by"
				elif expression == '+':
					statement = "plus"
				elif expression == '-':
					statement = "minus"
				else:
					statement = expression
	if len(statement) == 0:
		statement = "ERROR"
	print(statement)
	return statement

parsed = tokenize(File)
ordered = order(parsed)
print(ordered)
expression = ordered
location = []
statement = []
i = 0

while True:
	inp = ''
	char = stdscr.getch()
	if char == curses.KEY_LEFT:
		inp = "LEFT"
	elif char == curses.KEY_RIGHT:
		inp = "RIGHT"
	elif char == curses.KEY_UP:
		inp = "UP"
	elif char == curses.KEY_DOWN:
		inp = "DOWN"

	if len(inp) > 0:
		e = process_input(expression, location, inp)
		statement = to_speech(e, location).split(' ')
		i = 0

	if len(statement) != 0 and i < len(statement):
		os.system("say " + statement[i])		
		i += 1



