import pyttsx3, getch
engine = pyttsx3.init()
# File = open('test_latex.tex', 'r').read()

def parser(text):
	t = 0
	expressions = []
	while t < len(text):
		if text[t] == '$':
			new_expression = ''
			t += 1
			while text[t] != '$':
				if text[t] != ' ':
					new_expression += text[t]
				t += 1
			expressions += [new_expression]
			t += 1
		t += 1
	return expressions

# print(parser(File))

while True:
	char = getch.getch()
	print("$$$")
	print(char)