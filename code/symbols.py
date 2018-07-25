letters = 'qwertyuiopasdfghjklzxcvbnm'
greek_hebrew_letters = {'\\alpha': 'alpha', '\\beta': 'beta', '\\chi': 'chi', '\\delta': 'delta', '\\epsilon': 'epsilon', '\\eta': 'eta', '\\gamma': 'gamma', '\\iota': 'iota', '\\kappa': 'kappa', '\\lambda': 'lambda', '\\mu': 'mu', '\\nu': 'nu', '\\o': 'o', '\\omega': 'omega', '\\phi': 'phi', '\\pi': 'pi', '\\psi': 'psi', '\\rho': 'rho', '\\sigma': 'sigma', '\\tau': 'tau', '\\theta': 'theta', '\\upsilon': 'upsilon', '\\xi': 'xi', '\\zeta': 'zeta', '\\digamma': 'digamma', '\\varepsilon': 'varepsilon', '\\varkappa': 'varkappa', '\\varphi': 'varphi', '\\varrpi': 'varrpi', '\\varrho': 'varrho', '\\vargsigma': 'vargsigma', '\\vartheta': 'vartheta', '\\Delta': 'Capital Delta', '\\Gamma': 'Capital Gamma', '\\Lambda': 'Capital Lambda', '\\Omega': 'Capital Omega', '\\Phi': 'Capital Phi', '\\Pi': 'Capital Pi', '\\Psi': 'Capital Psi', '\\Sigma': 'Capital Sigma', '\\Theta': 'Capital Theta', '\\Upsilon': 'Capital Upsilon', '\\Xi': 'Capital Xi', '\\aleph': 'aleph', '\\beth': 'beth', '\\daleth': 'daleth', '\\gimel': 'gimel'}
numbers = '0123456789'
operations = '+-/*=^'
tex_operations = {'\\frac': 'frac', '\\sqrt': 'sqrt', '^': 'pow', '_': 'sub', '\\sin': 'sin', '\\cos': 'cos', '\\tan': 'tan', '\\cot': 'cot', '\\arcsin': 'arcsin', '\\arccos': 'arccos', '\\artan': 'arctan', '\\arccot': 'arccot', '\\sec': 'sec', '\\csc': 'csc'}
tex_base_term_opertations = {'\\times': '*', '\\pm': 'pm', '\\mp': 'mp', '\\div': '/', '\\ast': '*', '\\cdot': '*', '\\ne': 'ne', '\\approx': 'approx', '\\cong': 'cong', '\\equiv': 'equiv', '\\leq': 'leq', '\\geq': 'geq'}
all_tex_keys = {**tex_operations, **tex_base_term_opertations, **greek_hebrew_letters}

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
					'=': ["equals "],
					'_': ["sub"],
					'pm': ["plus or minus "],
					'mp': ["minus or plus"],
					'ne': ["not equal to "],
					'approx': ["is approximately equal to "],
					'cong': ["is congruent to "],
					'equiv': ["is equivalent to "],
					'>': ["is greater than "],
					'<': ["is less than "],
					'leq': ["is less than or equal to "],
					'geq': ["is greater than or equal to"]
				}.get(self.value, [self.value + ' '])

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
			if inner_term.right and (not inner_term.value or inner_term.value not in operations) and (not inner_term.right.value or inner_term.right.value not in operations):
				inner += ["times "]
			inner_term = inner_term.right
		output += [inner]
		return output

class expression(parenthetical):
	def __init__(self, targets, num = None):
		super().__init__(targets)
		self.num = num

	def spoken(self):
		if self.num:
			return ["expression " + str(self.num) + ' '] + super().spoken()
		else:
			return ["this is an expression "] + super().spoken()

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

class equation_list(term):
	def __init__(self, targets, num):
		super().__init__(targets)
		self.base_term = False
		self.num = num

	def spoken(self):
		return ["this is a list of " + str(self.num) + " equations "]

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
			return self.down.spoken() + ["over "] + self.down.right.right.spoken()
		elif self.down.base_term:
			return ["frac1"] + self.down.spoken() + ["divided by a term "]
		elif self.down.right.right.base_term: 
			return ["frac2"] + ["a term divided by "] + self.down.right.right.spoken()
		else:
			return ["a term divided by another term "]

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

class subscript(term):
	def __init__(self, targets, args):
		super().__init__(targets)

	def spoken(self):
		if self.base_term:
			return self.down.spoken() + ["sub "] + self.down.right.right.spoken()
		else:
			return ["a term sub "] + self.down.right.right.spoken()

	def fix(self):
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

class power(term):
	def __init__(self, targets, args):
		super().__init__(targets)

	def spoken(self):
		if self.base_term:
			return ["base "] + self.down.spoken()  + [" raised to the power of "] + self.down.right.right.spoken()
		elif self.down.base_term: 
			return ["base"] + self.down.spoken() + [" raised to the power of a term "]
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






