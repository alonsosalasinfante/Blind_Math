const numbers = '0123456789'
const greek_hebrew_letters = {'\\alpha': 'alpha', '\\beta': 'beta', '\\chi': 'chi', '\\delta': 'delta', '\\epsilon': 'epsilon', '\\eta': 'eta', '\\gamma': 'gamma', '\\iota': 'iota', '\\kappa': 'kappa', '\\lambda': 'lambda', '\\mu': 'mu', '\\nu': 'nu', '\\o': 'o', '\\omega': 'omega', '\\phi': 'phi', '\\pi': 'pi', '\\psi': 'psi', '\\rho': 'rho', '\\sigma': 'sigma', '\\tau': 'tau', '\\theta': 'theta', '\\upsilon': 'upsilon', '\\xi': 'xi', '\\zeta': 'zeta', '\\digamma': 'digamma', '\\varepsilon': 'varepsilon', '\\varkappa': 'varkappa', '\\varphi': 'varphi', '\\varrpi': 'varrpi', '\\varrho': 'varrho', '\\vargsigma': 'vargsigma', '\\vartheta': 'vartheta', '\\Delta': 'Capital Delta', '\\Gamma': 'Capital Gamma', '\\Lambda': 'Capital Lambda', '\\Omega': 'Capital Omega', '\\Phi': 'Capital Phi', '\\Pi': 'Capital Pi', '\\Psi': 'Capital Psi', '\\Sigma': 'Capital Sigma', '\\Theta': 'Capital Theta', '\\Upsilon': 'Capital Upsilon', '\\Xi': 'Capital Xi', '\\aleph': 'aleph', '\\beth': 'beth', '\\daleth': 'daleth', '\\gimel': 'gimel'}
const tex_operations = {'\\frac': 'frac', '\\sqrt': 'sqrt', '^': 'pow', '_': 'sub', '\\sin': 'sin', '\\cos': 'cos', '\\tan': 'tan', '\\cot': 'cot', '\\arcsin': 'arcsin', '\\arccos': 'arccos', '\\artan': 'arctan', '\\arccot': 'arccot', '\\sec': 'sec', '\\csc': 'csc'}
const tex_base_term_opertations = {'\\times': '*', '\\pm': 'pm', '\\mp': 'mp', '\\div': '/', '\\ast': '*', '\\cdot': '*', '\\ne': 'ne', '\\approx': 'approx', '\\cong': 'cong', '\\equiv': 'equiv', '\\leq': 'leq', '\\geq': 'geq'}
const all_tex_keys = Object.assign(tex_operations, tex_base_term_opertations, greek_hebrew_letters)
const all_operations = set(['^', '+', '-', '*', '/', '=', '_', 'pm', 'mp', 'ne', 'approx', 'cong', 'equiv', '>', '<', 'leq', 'geq'])

class term {
	/*
	The most base level linked term object form which all other terms are derived from
	all linked term objects have the following attributes:

		up, down, left, right: all of these attributes link to other term objects or null
		base_term: 	true or false depending on if the term object is a simple term, meaning 
					it is to be read out whole, or if it is a complex term, in which case
					term.spoken() will return "a term" or a similar abstraction
					All term type objects are by default base terms
		val: 	A string which is the term's actual value. Defaults to null for all other non 
				term type objects which derive from the term class
	*/
	constructor(targets, val = null) {
		this.up = targets[0]
		this.down = targets[1]
		this.left = targets[2]
		this.right = targets[3]
		this.base_term = true
		this.val = val
	}

	spoken() {
		/*
		The spoken method returns the statement to be read out
		when the user clicks one of the arrow keys and ends up
		on a new term object. The spoken methods should use 
		abstraction when describing a complex term

			Inputs: this is the term object
			Returns: 	a (usually nested) list of words to convert
						to spoken speech
		*/
		let res = {'^': "raised to the power of ",
					'+': "plus ",
					'-': "minus ",
					'*': "times ",
					'/': "divided by ",
					'=': ", equals ",
					'_': "sub ",
					'pm': "plus or minus ",
					'mp': "minus or plus ",
					'ne': "not equal to ",
					'approx': "is approximately equal to ",
					'cong': "is congruent to ",
					'equiv': "is equivalent to ",
					'>': "is greater than ",
					'<': "is less than ",
					'leq': "is less than or equal to ",
					'geq': "is greater than or equal to ",
					'A': "ey ",
					'a': "ey ",
					'y': "why ",
					'Y': "why "}
		if (this.val in res)
			return res[this.val]
		else
			return this.val + ' '
	}

	read_expression(r = true) {
		/*
		Function which returns a list of everything that is to be
		read under the hierarchical level of the calling term
		object. If r is true, everything to the right of the 
		calling term object, e.g. everything on the same heirarchial
		level but to the right of the selected term, is also 
		read. When using Blindreader.py, r is false for the 
		selected term, then all of the read_expression recursive
		calls that happen as a result of the first one defaults to
		r being true.

			Inputs: this is the calling term object
					r is whether or not to call read_expression for 
						term.right. true will do so, false will only 
						read out everything below the chosen term
			Returns: A nested list of everything to be read out
		*/
		if (this.val == '^' && r) {
			let res = {"2": "squared ", "3": "cubed "}
			if (this.right.val in res)
				return res[this.right.val)]
			else
				return "raised to the power of " + this.right.read_expression()
		}
		else if (this.val == "/" && r && this.left.val == "1"){
			let res = {	"2": "half ",
						"3": "third ",
						"4": "fourth ",
						"5": "fifth ",
						"6": "sixth ",
						"7": "seventh ",
						"8": "eighth ",
						"9": "ninth ",
						"10": "tenth "} 
			if (this.right.val in res)
				return res[this.right.val]
			else
				return "divided by " + this.right.read_expression()
		}
		else {
			let statement = this.spoken()
			if (r)
				this.check_right(statement)
			return statement
		}
	}

	check_right(statement) {
		/*
		Helper function which takes the passed in term object, 
		and appends the passed in statement whether appropriately.
		It will:	Add a "times " if needed
					Add the read_expression list of the right term
		*/
		if (this.right)
			if (this.add_times())
				statement += "times "
			statement += this.right.read_expression()
	}

	add_times() {
		/*
		Helper function which determines if the passed in term should have
		"times" after it and before the readout of the next term (e.g. if 
		you have "5(x+5)", it should read "5 TIMES quantity x + 5"). Used 
		in check_right 

			Inputs: A linked term object
			Returns: true or false
		*/
		if (this.right && (!(this instanceof term) || !all_operations.has(this.val)) && (!(this.right instanceof term) || !all_operations.has(this.right.val)))
			return true
		else
			return false
	}
}

class parenthetical extends term {
	constructor(targets) {
		super(targets)
		this.base_term = false
	}

	spoken() {
		let inner_term = this.down
		let output = ""
		while (inner_term != null) {
			if (inner_term.base_term)
				output += inner_term.spoken()
			else
				output += "a term "
			if (inner_term.add_times())
				output += "times "
			inner_term = inner_term.right
		}
		return output
	}

	read_expression(r = true) {
		let statement = "parenthetical"
		if (this.add_quantity())
			statement = "the quantity, "	
		statement += this.down.read_expression()
		if (this.add_quantity())
			statement += ', '
		if (r)
			this.check_right(statement)
		return statement
	}

	add_quantity() {
		/*
		Helper function which determines if the calling parenthetical
		term should have "the quantity " added before the rest of the
		read out. 

			Inputs: this is the calling parenthetical term object
			Returns: true or false if "the quantity " should be added
		*/
		if (this instanceof expression)
			return false
		else if (this.down instanceof frac)
			return false
		else if (this.up instanceof subscript || this.up instanceof frac)
			return false
		else
			return true
	}
}

class expression extends parenthetical {
	constructor(targets, num = null) {
		super(targets)
		this.num = num
	}

	spoken() {
		if (this.num)
			return "expression " + str(this.num) + ', ' + super()
		else
			return "this is an expression, " + super()
	}

	read_expression(r = true) {
		if (this.num)
			statement = "expression " + str(this.num) + ', ' + super(r)
		else
			statement = "this is an expression, " + this.down.read_expression()
		return statement
	}
}

class equation extends term {
	constructor(targets) {
		super(targets)
		this.base_term = false
	}

	spoken() {
		let output = "this is an equation, "
		let expression = this.down
		while (expression != null) {
			output += expression.spoken()
			expression = expression.right
		}
		return output
	}

	read_expression(r = true) {
		let statement = "this is an equation, " + this.down.read_expression()
		return statement
	}
}

class equation_list extends term {
	constructor(targets, num) {
		super(targets)
		this.base_term = false
		this.num = num
	}

	spoken() {
		return "this is a list of " + this.num + " equations "
	}

	read_expression(r = true) {
		let statement = this.spoken()
		if (r)
			this.check_right(statement)
		return statement
	}
}

class frac extends term {
	constructor(targets, args) {
		let down = args[0]
		down.right = new term([null, null, down, args[1]], '/')
		args[1].left = down.right
		targets[1] = down
		super(targets)
		this.num = this.down
		this.den = this.down.right.right
		if (!(this.num.base_term && this.den.base_term))
			this.base_term = false 
	}

	spoken() {
		if (this.base_term) {
			if (this.num.val == "1") {
				let res = {	"2": "one half ",
							"3": "one third ",
							"4": "one fourth ",
							"5": "one fifth ",
							"6": "one sixth ",
							"7": "one seventh ",
							"8": "one eighth ",
							"9": "one ninth ",
							"10": "one tenth "}
				if (this.den.val in res)
					return res[this.den.val]
				else
					return this.num.spoken() + "over " + this.den.spoken()
			}
			else
				return this.num.spoken() + "over " + this.den.spoken()
		}
		else if (this.num.base_term)
			return this.num.spoken() + ", divided by a term "
		else if (this.den.base_term)
			return "a term divided by, " + this.den.spoken()
		else
			return "a term divided by another term "
	}

	read_expression(r = true) {
		if (this.base_term)
			statement = this.num.read_expression()
		else
			statement = "the numerator, " + this.num.read_expression(false) + "over the denominator, " + this.den.read_expression(false)
		if (r)
			this.check_right(statement)
		return statement
	}
}

class sqrt extends term {
	constructor(targets, args) {
		targets[1] = args[0]
		super(targets)
		if (!this.down.base_term)
			this.base_term = false
	}

	spoken() {
		if (this.base_term)
			return "The square root of, " + this.down.spoken()
		else
			return "The square root of a parenthetical term "
	}

	read_expression(r = true) {
		statement = "The square root of " + this.down.read_expression()
		if (r)
			this.check_right(statement)
		return statement
	}
}

class subscript extends term {
	constructor(targets, args) {
		super(targets)
	}

	fix() {
		/*
		Helper method which only some term orbjects (currently only
		subscript and power) have due to them having to include the
		term behind them as well as the one in the front (e.g. x_n should
		have x as well as n in its arguments, but the only way to do this
		is after parsing/terminization). This method takes the subscript
		term object, changes the left and right objects pointers to skip
		over the immediate appropriate # of left/right objects, includes
		them as a pseudo-parenthetical linked objects under the down pointer 

			Input: this is the calling term-object
		*/
		if (this.left.left)
			this.left.left.right = this
		else
			this.left.up.down = this		
			
		this.down = this.left
		this.left = this.left.left
		this.down.up = this
		this.down.left = null
		this.down.right = term([this, null, this.down, this.right], '_')

		if (this.right.right)
			this.right.right.left = this
		this.right = this.right.right
		this.down.right.right.left = this.down.right
		this.down.right.right.up = this
		this.down.right.right.right = null

		if (!this.down.base_term)
			this.base_term = false
	}

	spoken() {
		if (this.base_term)
			return this.down.spoken() + "sub " + this.down.right.right.spoken()
		else
			return "a term sub " + this.down.right.right.spoken()
	}

	read_expression(r = true) {
		statement = this.down.read_expression()
		if (r)
			this.check_right(statement)
		return statement
	}
}

class power extends term {
	constructor(targets, args) {
		super(targets)
	}

	fix() {
		if (this.left.left)
			this.left.left.right = this
		else
			this.left.up.down = this		
			
		this.down = this.left
		this.left = this.left.left
		this.down.up = this
		this.down.left = null
		this.down.right = term([this, null, this.down, this.right], '^')

		if (this.right.right)
			this.right.right.left = this
		this.right = this.right.right
		this.down.right.right.left = this.down.right
		this.down.right.right.up = this
		this.down.right.right.right = null

		if (!(this.down.base_term && this.down.right.right.base_term))
			this.base_term = false
	}

	spoken() {
		if (this.base_term) {
			if (this.down.right.right.val == "2")
				return this.down.spoken() + "squared "
			else if (this.down.right.right.val == "3")
				return this.down.spoken() + "cubed "
			else
				return this.down.spoken()  + "raised to the power of, " + this.down.right.right.spoken()
		}
		else if (this.down.base_term) 
			return this.down.spoken() + "raised to the power of a term "
		else if (this.down.right.right.base_term)
			return "A base term raised to the power of, " + this.down.right.right.spoken()
		else
			return "A base term raised to the power of another term "
	}

	read_expression(r = true) {
		statement = this.down.read_expression() 
		if (r)
			this.check_right(statement)
		return statement
	}
}

class trig extends term {
	constructor(targets, args, op) {
		targets[1] = args[0]
		super(targets)
		this.operation = op
		if (!this.down.base_term)
			this.base_term = false
	}

	spoken() {
		if (this.base_term)
			return this.operation + " of " + this.down.spoken()
		else 
			return this.operation + " of a term "
	}

	read_expression(r = true) {
		statement = this.operation, " of " + this.down.read_expression()
		if (r)
			this.check_right(statement)
		return statement
	}
}

class cos extends trig {constructor(targets, args) {super(targets, args, 'cosine')}}
class sin extends trig {constructor(targets, args) {super(targets, args, 'sine')}}
class tan extends trig {constructor(targets, args) {super(targets, args, 'tangent')}}
class cot extends trig {constructor(targets, args) {super(targets, args, 'cotangent')}}
class arccos extends trig {constructor(targets, args) {super(targets, args, 'arc cosine')}}
class arcsin extends trig {constructor(targets, args) {super(targets, args, 'arc sine')}}
class arctan extends trig {constructor(targets, args) {super(targets, args, 'arc tangent')}}
class arccot extends trig {constructor(targets, args) {super(targets, args, 'arc cotangent')}}
class sec extends trig {constructor(targets, args) {super(targets, args, 'secant')}}
class csc extends trig {constructor(targets, args) {super(targets, args, 'cosecant')}}

const tex_args = {'frac': [frac, 2], 'sqrt': [sqrt, 1], 'pow': [power, 0], 'sub': [subscript, 0], 'cos': [cos, 1], 'sin': [sin, 1], 'tan': [tan, 1], 'cot': [cot, 1], 'arccos': [arccos, 1], 'arcsin': [arcsin, 1], 'arctan': [arctan, 1], 'arccot': [arccot, 1], 'sec': [sec, 1], 'csc': [csc, 1]}
const object_fixes = Object.assign(subscript, power)