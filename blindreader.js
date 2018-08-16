import * as symbols from './symbols.js'

export function tokenize(text) {
	/*
	Tokenizer function which deletes whitespace and separates all important tokens
	for any mathematical expressions in the LaTeX document
	
		Inputs: text is the entire LaTeX document in plaintext
		Returns: an list of all relevent tokens of each math expression found
	*/
	let i = 0 // Index
	let tokens = []

	while (i < text.length) {
		if (text[i] == '$' || text.substr(i,2) == '\\[') { // Start sequence for LaTeX math mode
			if (text[i] == '$')
				i += 1
			else if (text.substr(i,2) == '\\[')
				i += 2
			tokens.push('(')
			while (text[i] != '$' && text.substr(i,2) != '\\[') { // End sequence for LaTeX math mode
				if (text[i] == '=')
					tokens = tokens.concat([')'], [text[i]], ['('])
				else if (text[i] == '{')
					tokens.push('(')
				else if (text[i] == '}')
					tokens.push(')')
				else if (text[i] == '\\') { // Escape sequence for most LaTeX special characters
					for (let key in symbols.all_tex_keys) {
						if (text.substr(i, key.length) == key) {
							tokens.push(symbols.all_tex_keys[key])
							i += key.length - 1 
							break
						}
					}
				}
				else if (text[i] in symbols.all_tex_keys)
					tokens.push(symbols.all_tex_keys[text[i]])
				else if (!'\n '.includes(text[i])) { // Catching all valid numbers
					let term = text[i]
					if (symbols.numbers.includes(term)) {
						i += 1
						while (symbols.numbers.includes(text[i])) {
							term += text[i]
							i += 1
						}
						i -= 1
					}
					tokens.push(term)
				}
				i += 1
			}
			tokens.push(')')
		}
		i += 1
	}
	return tokens
}

export function order(tokens) {
	/*
	Function which first parses the math tokens and creates nested 
	lists for any parenthetical terms/function arguments and rearranges
	function arguments then creates linked term objects
	
		Inputs: Math expression token list from tokenize function
		Returns: A linked equation_list object
	*/
	let expression = []
	let index = 0
	while (index < tokens.length) {
		let parse_res = parse(tokens, index)
		let inner_expression = parse_res[0]
		index = parse_res[1]
		if (!(inner_expression == null))
			expression.push(inner_expression)
	}
	console.log(expression, "after parse")
	expression = terminize(new Set([]), expression, [], true)
	console.log(expression, "after terminize")
	fix_terms(expression)
	return expression
}

export function parse(token, index) {
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
			index = parse_res[1]
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

export function terminize(checked, expressions, loc, arg = false) {
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
		return terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[loc.length-1]+1))
	else
		checked.add(JSON.stringify(loc))

	let expression = expressions
	let i = 0
	let res
	while (i < loc.length - 1) {
		expression = expression[loc[i]]
		if (expression == undefined)
			return null
		i += 1
	}
	if (loc.length > 0 && expression[loc[loc.length-1]] == undefined) {
		return null
	}

	let targets = [null, null, null, null]

	if (loc.length == 0 || Array.isArray(expression[loc[loc.length-1]])) {
		targets[1] = terminize(checked, expressions, loc.concat([0]))
		if (!arg) // Arguments do not have right expressions
			targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[loc.length-1]+1))
		if (arg && loc.length > 0 && expression[loc[loc.length-1]].length == 1) // Single listed arguments are treated as terms
			res = new symbols.term(targets, expression[loc[loc.length-1]][0])
		else if (loc.length == 0) { // Expression/Equation differentiation
			if (expression.length == 1) {
				targets[1] = targets[1].down
				res = new symbols.expression(targets)
			}
			else {
				res = new symbols.equation(targets)
			}
		}
		else if (loc.length == 1 && expression.includes("=")) // Numbered expressions within equations
			res = new symbols.expression(targets, Math.floor(loc[loc.length-1]/2)+1)
		else // Parentheticals
			res = new symbols.parenthetical(targets)
	}
	else if (expression[loc[loc.length-1]] in symbols.tex_args) { // LaTeX specific keywords
		let args = symbols.tex_args[expression[loc[loc.length-1]]] // Function and number of arguments
		let func = args[0]
		let arg = args[1]
		args = expression.slice(loc[loc.length-1]+1, loc[loc.length-1]+1+arg)
		for (i = 0; i < arg; i ++)
			args[i] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[loc.length-1]+1+i), true) // Terminize all arguments
		targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[loc.length-1]+1+arg)) // Get the right expression
		res = new func(targets, args)
	}
	else { // All other terms
		if (!arg)
			targets[3] = terminize(checked, expressions, loc.slice(0, loc.length-1).concat(loc[loc.length-1] + 1))
		res = new symbols.term(targets, expression[loc[loc.length-1]])
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

export function fix_terms(term) {
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