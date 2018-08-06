greek_hebrew_letters = {'\\alpha': 'alpha', '\\beta': 'beta', '\\chi': 'chi', '\\delta': 'delta', '\\epsilon': 'epsilon', '\\eta': 'eta', '\\gamma': 'gamma', '\\iota': 'iota', '\\kappa': 'kappa', '\\lambda': 'lambda', '\\mu': 'mu', '\\nu': 'nu', '\\o': 'o', '\\omega': 'omega', '\\phi': 'phi', '\\pi': 'pi', '\\psi': 'psi', '\\rho': 'rho', '\\sigma': 'sigma', '\\tau': 'tau', '\\theta': 'theta', '\\upsilon': 'upsilon', '\\xi': 'xi', '\\zeta': 'zeta', '\\digamma': 'digamma', '\\varepsilon': 'varepsilon', '\\varkappa': 'varkappa', '\\varphi': 'varphi', '\\varrpi': 'varrpi', '\\varrho': 'varrho', '\\vargsigma': 'vargsigma', '\\vartheta': 'vartheta', '\\Delta': 'Capital Delta', '\\Gamma': 'Capital Gamma', '\\Lambda': 'Capital Lambda', '\\Omega': 'Capital Omega', '\\Phi': 'Capital Phi', '\\Pi': 'Capital Pi', '\\Psi': 'Capital Psi', '\\Sigma': 'Capital Sigma', '\\Theta': 'Capital Theta', '\\Upsilon': 'Capital Upsilon', '\\Xi': 'Capital Xi', '\\aleph': 'aleph', '\\beth': 'beth', '\\daleth': 'daleth', '\\gimel': 'gimel'}
numbers = '0123456789'
operations = '+-/*=^'
tex_operations = {'\\frac': 'frac', '\\sqrt': 'sqrt', '^': 'pow', '_': 'sub', '\\sin': 'sin', '\\cos': 'cos', '\\tan': 'tan', '\\cot': 'cot', '\\arcsin': 'arcsin', '\\arccos': 'arccos', '\\artan': 'arctan', '\\arccot': 'arccot', '\\sec': 'sec', '\\csc': 'csc'}
tex_base_term_opertations = {'\\times': '*', '\\pm': 'pm', '\\mp': 'mp', '\\div': '/', '\\ast': '*', '\\cdot': '*', '\\ne': 'ne', '\\approx': 'approx', '\\cong': 'cong', '\\equiv': 'equiv', '\\leq': 'leq', '\\geq': 'geq'}
all_tex_keys = {**tex_operations, **tex_base_term_opertations, **greek_hebrew_letters}
all_operations = {'^', '+', '-', '*', '/', '=', '_', 'pm', 'mp', 'ne', 'approx', 'cong', 'equiv', '>', '<', 'leq', 'geq'}

class term():
	'''
	The most base level linked term object form which all other terms are derived from
	all linked term objects have the following attributes:

		up, down, left, right: all of these attributes link to other term objects or None
		base_term: 	True or False depending on if the term object is a simple term, meaning 
					it is to be read out whole, or if it is a complex term, in which case
					term.spoken() will return "a term" or a similar abstraction
					All term type objects are by default base terms
		value: 	A string which is the term's actual value. Defaults to None for all other non 
				term type objects which derive from the term class
	'''
	def __init__(self, targets, value = None):
		self.up, self.down, self.left, self.right = targets 
		self.base_term = True
		self.value = value

	def spoken(self):
		'''
		The spoken method returns the statement to be read out
		when the user clicks one of the arrow keys and ends up
		on a new term object. The spoken methods should use 
		abstraction when describing a complex term

			Inputs: self is the term object
			Returns: 	a (usually nested) list of words to convert
						to spoken speech
		'''
		return {	'^': ["raised to the power of "],
					'+': ["plus "],
					'-': ["minus "],
					'*': ["times "],
					'/': ["divided by "],
					'=': ["equals "],
					'_': ["sub "],
					'pm': ["plus or minus "],
					'mp': ["minus or plus "],
					'ne': ["not equal to "],
					'approx': ["is approximately equal to "],
					'cong': ["is congruent to "],
					'equiv': ["is equivalent to "],
					'>': ["is greater than "],
					'<': ["is less than "],
					'leq': ["is less than or equal to "],
					'geq': ["is greater than or equal to "],
					'A': ["ey "],
					'a': ["ey "],
					'y': ["why "],
					'Y': ["why "]
				}.get(self.value, [self.value + ' '])

	def read_expression(self, r = True):
		'''
		Function which returns a list of everything that is to be
		read under the hierarchical level of the calling term
		object. If r is True, everything to the right of the 
		calling term object, e.g. everything on the same heirarchial
		level but to the right of the selected term, is also 
		read. When using Blindreader.py, r is False for the 
		selected term, then all of the read_expression recursive
		calls that happen as a result of the first one defaults to
		r being True.

			Inputs: self is the calling term object
					r is whether or not to call read_expression for 
						term.right. True will do so, False will only 
						read out everything below the chosen term
			Returns: A nested list of everything to be read out
		'''
		if self.value == '^' and r:
			return {"2": ["squared "],
					"3": ["cubed "]
					}.get(self.right.value, ["raised to the power of "] + self.right.read_expression())
		elif self.value == "/" and r and self.left.value == "1":
			return {"2": ["half "],
					"3": ["third "],
					"4": ["fourth "],
					"5": ["fifth "],
					"6": ["sixth "],
					"7": ["seventh "],
					"8": ["eighth "],
					"9": ["ninth "],
					"10": ["tenth "]
					}.get(self.right.value, ["divided by "] + self.right.read_expression())
		else:
			statement = self.spoken()
			if r:
				self.check_right(statement)
			return statement

	def check_right(self, statement):
		'''
		Helper function which takes the passed in term object, 
		and appends the passed in statement whether appropriately.
		It will:	Add a comma if needed due to an "="
					Add a "times " if needed
					Add the read_expression list of the right term
		'''
		if self.right:
			if self.right.value == "=":
				statement += [', ']
			elif self.add_times():
				statement += ["times "]
			statement += self.right.read_expression()

	def add_times(self):
		'''
		Helper function which determines if the passed in term should have
		"times" after it and before the readout of the next term (e.g. if 
		you have "5(x+5)", it should read "5 TIMES quantity x + 5"). Used 
		in check_right 

			Inputs: A linked term object
			Returns: True or False
		'''
		if self.right and (type(self) != term or (self.value not in all_operations)) and (type(self.right) != term or (self.right.value not in all_operations)):
			return True
		else:
			return False

class parenthetical(term):
	def __init__(self, targets):
		super().__init__(targets)
		self.base_term = False

	def spoken(self):
		inner_term = self.down
		output  = ["parenthetical"]
		inner = []
		while inner_term != None:
			if inner_term.base_term:
				inner += inner_term.spoken()
			else:
				inner += ["a term "]
			if inner_term.add_times():
				inner += ["times "]
			inner_term = inner_term.right
		output += [inner]
		return output

	def read_expression(self, r = True):
		statement = ["parenthetical"]
		if self.add_quantity():
			inner = ["the quantity, "]
		else:
			inner = []	
		inner += self.down.read_expression()
		if self.add_quantity():
			inner += [', ']
		if r:
			self.check_right(inner)
		statement += [inner]
		return statement

	def add_quantity(self):
		'''
		Helper function which determines if the calling parenthetical
		term should have "the quantity " added before the rest of the
		read out. 

			Inputs: self is the calling parenthetical term object
			Returns: True or False if "the quantity " should be added
		'''
		if type(self) == expression:
			return False
		elif type(self.down) in (frac,):
			return False
		elif type(self.up) in (subscript, frac):
			return False
		else:
			return True

class expression(parenthetical):
	def __init__(self, targets, num = None):
		super().__init__(targets)
		self.num = num

	def spoken(self):
		if self.num:
			return ["expression " + str(self.num) + ' '] + super().spoken()
		else:
			return ["this is an expression "] + super().spoken()

	def read_expression(self, r = True):
		if self.num:
			statement = ["expression " + str(self.num) + ', '] + super().read_expression(r)
		else:
			statement = ["this is an expression, "] + self.down.read_expression()
		return statement

class equation(term):
	def __init__(self, targets):
		super().__init__(targets)
		self.base_term = False

	def spoken(self):
		output = ["this is an equation "]
		expression = self.down
		while expression != None:
			output += expression.spoken()
			expression = expression.right
		return output

	def read_expression(self, r = True):
		statement = ["this is an equation, "] + self.down.read_expression()
		return statement

class equation_list(term):
	def __init__(self, targets, num):
		super().__init__(targets)
		self.base_term = False
		self.num = num

	def spoken(self):
		return ["this is a list of " + str(self.num) + " equations "]

	def read_expression(self, r = True):
		statement = self.spoken()
		if r:
			self.check_right(statement)
		return statement

class frac(term):
	def __init__(self, targets, args):
		down = args[0]
		down.right = term([None, None, down, args[1]], '/')
		args[1].left = down.right
		targets[1] = down
		super().__init__(targets)
		self.num, self.den = self.down, self.down.right.right
		if not (self.num.base_term and self.den.base_term):
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			if self.num.value == "1":
				return {"2": ["one half "],
						"3": ["one third "],
						"4": ["one fourth "],
						"5": ["one fifth "],
						"6": ["one sixth "],
						"7": ["one seventh "],
						"8": ["one eighth "],
						"9": ["one ninth "],
						"10": ["one tenth "]
						}.get(self.den.value, self.num.spoken() + ["over "] + self.den.spoken())
			else:
				return self.num.spoken() + ["over "] + self.den.spoken()
		elif self.num.base_term:
			return self.num.spoken() + ["divided by a term "]
		elif self.den.base_term: 
			return ["a term divided by "] + self.den.spoken()
		else:
			return ["a term divided by another term "]

	def read_expression(self, r = True):
		if self.base_term:
			statement = self.num.read_expression()
		else:
			statement = ["the numerator, "] + self.num.read_expression(False) + ["over the denominator, "] + self.den.read_expression(False)
		if r:
			self.check_right(statement)
		return statement

class sqrt(term):
	def __init__(self, targets, args):
		targets[1] = args[0]
		super().__init__(targets)
		if not self.down.base_term:
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return ["The square root of "] + self.down.spoken()
		else:
			return ["The square root of a parenthetical term "]

	def read_expression(self, r = True):
		statement = ["The square root of "] + self.down.read_expression()
		if r:
			self.check_right(statement)
		return statement

class subscript(term):
	def __init__(self, targets, args):
		super().__init__(targets)

	def spoken(self):
		if self.base_term:
			return self.down.spoken() + ["sub "] + self.down.right.right.spoken()
		else:
			return ["a term sub "] + self.down.right.right.spoken()

	def fix(self):
		'''
		Helper method which only some term orbjects (currently only
		subscript and power) have due to them having to include the
		term behind them as well as the one in the front (e.g. x_n should
		have x as well as n in its arguments, but the only way to do this
		is after parsing/terminization). This method takes the subscript
		term object, changes the left and right objects pointers to skip
		over the immediate appropriate # of left/right objects, includes
		them as a pseudo-parenthetical linked objects under the down pointer 

			Input: self is the callinf term-object
		'''
		if self.left.left:
			self.left.left.right = self
		else:
			self.left.up.down = self		
			
		self.down = self.left
		self.left = self.left.left
		self.down.up = self
		self.down.left = None
		self.down.right = term([self, None, self.down, self.right], '_')

		if self.right.right:
			self.right.right.left = self
		self.right = self.right.right
		self.down.right.right.left = self.down.right
		self.down.right.right.up = self
		self.down.right.right.right = None

		if not self.down.base_term:
			self.base_term = False

	def read_expression(self, r = True): 
		statement = self.down.read_expression()
		if r:
			self.check_right(statement)
		return statement

class power(term):
	def __init__(self, targets, args):
		super().__init__(targets)

	def spoken(self):
		if self.base_term:
			if self.down.right.right.value == "2":
				return self.down.spoken() + ["squared "]
			elif self.down.right.right.value == "3":
				return self.down.spoken() + ["cubed "]
			else:
				return ["base "] + self.down.spoken()  + ["raised to the power of "] + self.down.right.right.spoken()
		elif self.down.base_term: 
			return ["base "] + self.down.spoken() + ["raised to the power of a term "]
		elif self.down.right.right.base_term:
			return ["A base term raised to the power of "] + self.down.right.right.spoken()
		else:
			return ["A base term raised to the power of another term "]

	def fix(self):
		if self.left.left:
			self.left.left.right = self
		else:
			self.left.up.down = self		
			
		self.down = self.left
		self.left = self.left.left
		self.down.up = self
		self.down.left = None
		self.down.right = term([self, None, self.down, self.right], '^')

		if self.right.right:
			self.right.right.left = self
		self.right = self.right.right
		self.down.right.right.left = self.down.right
		self.down.right.right.up = self
		self.down.right.right.right = None

		if not (self.down.base_term and self.down.right.right.base_term):
			self.base_term = False

	def read_expression(self, r = True):
		statement = self.down.read_expression() 
		if r:
			self.check_right(statement)
		return statement

class trig(term):
	def __init__(self, targets, args, op):
		targets[1] = args[0]
		super().__init__(targets)
		self.operation = op
		if not self.down.base_term:
			self.base_term = False 

	def spoken(self):
		if self.base_term:
			return [self.operation, " of "] + self.down.spoken()
		else:
			return [self.operation, " of a term "]

	def read_expression(self, r = True): 
		statement = [self.operation, " of "] + self.down.read_expression()
		if r:
			self.check_right(statement)
		return statement

class cos(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'cosine')

class sin(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'sine')

class tan(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'tangent')

class cot(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'cotangent')

class arccos(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'arc cosine')

class arcsin(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'arc sine')

class arctan(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'arc tangent')

class arccot(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'arc cotangent')

class sec(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'secant')

class csc(trig):
	def __init__(self, targets, args):
		super().__init__(targets, args, 'cosecant')

tex_args = {'frac': (frac, 2), 'sqrt': (sqrt, 1), 'pow': (power, 0), 'sub': (subscript, 0), 'cos': (cos, 1), 'sin': (sin, 1), 'tan': (tan, 1), 'cot': (cot, 1), 'arccos': (arccos, 1), 'arcsin': (arcsin, 1), 'arctan': (arctan, 1), 'arccot': (arccot, 1), 'sec': (sec, 1), 'csc': (csc, 1)}
object_fixes = {subscript, power}