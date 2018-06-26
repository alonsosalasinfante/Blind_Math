letters = 'qwertyuiopasdfghjklzxcvbnm'
# greek_hebrew_letters = {'\\alpha', '\\beta', '\\chi', '\\delta', '\\epsilon', '\\eta', '\\gamma', '\\iota', '\\kappa', '\\lambda', '\\mu', '\\nu', 'o', '\\omega', '\\phi', '\\pi', '\\psi', '\\rho', '\\sigma', '\\tau', '\\theta', '\\upsilon', '\\xi', '\\zeta', '\\digamma', '\\varepsilon', '\\varkappa', '\\varphi', '\\varrpi', '\\varrho', '\\vargsigma', '\\vartheta', '\\Delta', '\\Gamma', '\\Lambda', '\\Omega', '\\Phi', '\\Pi', '\\Psi', '\\Sigma', '\\Theta', '\\Upsilon', '\\Xi', '\\aleph', '\\beth', '\\daleth', '\\gimel'}
numbers = '0123456789'
operations = '+-/*'
tex_operations = {'\\frac': 'frac', '\\sqrt': 'sqrt', '^': 'pow'}
tex_base_term_opertations = {'\\times': 'times', '\\pm': 'pm', '\\mp': 'mp', '\\div': 'div', '\ast': 'ast', '\\cdot': 'cdot'}
all_tex_keys = {**tex_operations, **tex_base_term_opertations}

class term():
	def __init__(self, targets, value = None):
		self.up, self.down, self.left, self.right = targets 
		self.base_term = True
		self.value = value

	def spoken(self):
		return {	'^': ["raised to the power of "],
					'+': ["plus "],
					'-': ["minus "],
					'*': ["times "],
					'/': ["divided by "],
					'=': ["equals "]
				}.get(self.value, [self.value + ' '])

class parenthetical(term):
	def __init__(self, targets):
		super().__init__(targets)

	def spoken(self):
		inner_term = self.down
		string  = ["parenthetical"]
		inner = []
		while inner_term != None:
			if inner_term.base_term:
				inner += inner_term.spoken()
			else:
				inner += "a term "
			inner_term = inner_term.right
		string += [inner]
		return string

class frac(term):
	def __init__(self, targets, args):
		down = args[0]
		down.right = term([None, None, down, args[1]], '/')
		args[1].left = down.right
		targets[1] = down
		super().__init__(targets)
		if not (self.down.base_term and self.down.right.right.base_term):
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return self.down.spoken() + ["divided by "] + self.down.right.right.spoken()
		elif self.down.base_term:
			return ["frac"] + self.down.spoken() + ["divided by a term "]
		elif self.down.right.right.base_term: 
			return ["frac"] + ["a term divided by "] + self.down.right.right.spoken()
		else:
			return ["a term divided by another term "]

class sqrt(term):
	def __init__(self, targets):
		super().__init__(targets)
		if not self.down.base_term:
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return ["The square root of "] + self.down.spoken()
		else:
			return ["The square root of a parenthetical term "]

class power(term):
	def __init__(self, targets, args):
		down = args[0]
		down.right = term([None, None, down, args[1]], '^')
		args[1].left = down.right
		targets[1] = down
		super().__init__(targets)
		if not (self.down.base_term and self.down.right.base_term):
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return self.down.spoken()  + [" raised to the power of "] + self.down.right.right.spoken()
		elif self.down.base_term: 
			return self.down.spoken() + [" raised to the power of a term "]
		elif self.down.right.right.base_term:
			return ["A term raised to the power of "] + self.down.right.right.spoken()
		else:
			return ["A term raised to the power of another term "]

class trig(term):
	def __init__(self, targets, args):
		super().__init__(targets)
		self.operation = args[0]
		if not self.down.base_term:
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return [op, " of "] + self.down.spoken()
		else:
			return [op, " of a term "]

tex_args = {'frac': (frac, 2), 'sqrt': (sqrt, 1), 'pow': (power, 2)}