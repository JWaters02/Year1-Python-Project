#from prettytable import PrettyTable
import itertools

# ====================== 
# Backus-Naur Form

#<expression> ::= <term> ( <or_symbol> <term> )...
#<or_symbol> ::= "+" | "or"
#<term> ::= <symbol> ( ("." | "and") <symbol> )...
#<symbol> ::= <not_symbol> | <parenthesized_symbol> | <variable> | <literal>
#<not_symbol> ::= "!" <symbol>
#<parenthesized_symbol> ::= "(" <expression> ")"
#<variable> ::= a letter
#<literal> ::= "0" | "1"

# ====================== 


# Evalutates not symbols
class NotExpression:
    def __init__(self, sub_symbol):
        self.sub_symbol = sub_symbol

    def evaluate(self, context):
        return not self.sub_symbol.evaluate(context)


# Evaluates and terms
class AndExpression:
    def __init__(self, and_list):
        self.and_list = and_list

    def evaluate(self, context):
        for term in self.and_list:
            if not term.evaluate(context):
                return False
        return True


# Evaluates or expressions
class OrExpression:
    def __init__(self, expression_list):
        self.expression_list = expression_list

    def evaluate(self, context):
        for expr in self.expression_list:
            if expr.evaluate(context):
                return True
        return False


# Evaluates parentheses in the expression
class ParenthesizedSymbol:
    def __init__(self, sub_expr):
        self.sub_expr = sub_expr
    
    def evaluate(self, context):
        return self.sub_expr.evaluate(context)


# Evaluates any variables
class VariableSymbol:
    def __init__(self, letter):
        self.letter = letter
    
    def evaluate(self, context):
        return context[self.letter]


# Evaluates any literals
class LiteralSymbol:
    def __init__(self, literal):
        self.literal = literal
    
    def evaluate(self, context):
        return self.literal


# Parses each section of the expression into a usable state
class Parser:
    def __init__(self, text):
        self.text = text.replace(' ', '') # Removes whitespace
        self.pos = 0
        self.variables = set() # Tracks all the variables in the expression
        self.NOT_ALTERNATIVES = [
            '!', 'not', '¬', '-'
        ]
        self.OR_ALTERNATIVES = [
            '+', 'or', '|', 'v'
        ]
        self.AND_ALTERNATIVES = [
            '.', 'and', '^', '&'
        ]

    # Reads the tokens of the expression by iterating through the position
    def consume_token(self):
        # If end of string
        if self.pos >= len(self.text):
            return None # None = special token
        # If the text at current position is a letter
        elif self.text[self.pos].isalpha():
            ret = ''
            # Loop through all letters in text
            while self.pos < len(self.text) and self.text[self.pos].isalpha():
                ret += self.text[self.pos]
                self.pos += 1
            return ret
        else:
            ret = self.text[self.pos]
            self.pos += 1
            return ret

    # Reads the token of the expression at current position
    def peek_token(self):
        prevPos = self.pos
        ret = self.consume_token()
        self.pos = prevPos
        return ret

    # Parsed expression
    def parse(self):
        ret = self.parse_or()
        if self.consume_token() is not None:
            raise Exception('Parse error')
        return ret

    # Returns the or of expression
    def parse_or(self):
        terms = []
        terms.append(self.parse_and())
        token = self.peek_token()
        while token in self.OR_ALTERNATIVES:
            token = self.consume_token()
            terms.append(self.parse_and())
            token = self.peek_token()
        ret = OrExpression(terms)
        return ret

    # Returns the and term of expression
    def parse_and(self):
        terms = []
        terms.append(self.parse_symbol())
        token = self.peek_token()
        while token in self.AND_ALTERNATIVES:
            token = self.consume_token()
            terms.append(self.parse_symbol())
            token = self.peek_token()
        ret = AndExpression(terms)
        return ret

    # If next pos is open bracket then parse parenthesis
    # If next pos is not then parse not
    # If next pos is literal then set true or false
    # If next pos is variable then parse variable symbol
    def parse_symbol(self):
        token = self.peek_token()
        if token == "(":
            return self.parse_parenthesized_symbol()
        elif token in self.NOT_ALTERNATIVES:
            return self.parse_not()
        elif token == "1" or token == "0":
            return self.parse_literal()
        else:
            return self.parse_variable_symbol()

    # Returns the not of the expression
    def parse_not(self):
        token = self.consume_token()
        if not token in self.NOT_ALTERNATIVES:
            raise Exception('Invalid syntax')
        sub_symbol = self.parse_symbol()
        ret = NotExpression(sub_symbol)
        return ret

    # Returns the expression within the parentheses
    # Errors if either parentheses missing
    def parse_parenthesized_symbol(self):
        token = self.consume_token()
        if not token == "(":
            raise Exception('Missing (')
        ret = ParenthesizedSymbol(self.parse_or())
        token = self.consume_token()
        if not token == ")":
            raise Exception('Missing )')
        return ret

    # Returns any variables in the expression/term
    # Raises an error if the variable is not text
    def parse_variable_symbol(self):
        name = self.consume_token()
        if not name.isalpha():
            raise Exception('Variable not detected')
        self.variables.add(name)
        return VariableSymbol(name)

    # Returns if literal is true or false
    def parse_literal(self):
        token = self.consume_token()
        if not token == "1" and not token == "0":
            raise Exception('Incorrect syntax')
        if token == "1":
            literal = True
        else:
            literal = False
        ret = LiteralSymbol(literal)
        return ret

# generate the context variables from parser.variables.
# e.g. 
# a | b
# 0 | 0
# 0 | 1
# 1 | 0
# 1 | 1
# parser = Parser(text="!((a+b).0)")
# ast = parser.parse()
# context = {'a': False, 'b': False}
# print(ast.evaluate(context))
# context = {'a': False, 'b': True}
# print(ast.evaluate(context))
# context = {'a': True, 'b': False}
# print(ast.evaluate(context))
# context = {'a': True, 'b': True}
# print(ast.evaluate(context))
# or
# e | x | i
# 0 | 0 | 0
# 0 | 1 | 0
# 1 | 0 | 0
# 1 | 1 | 0
# 0 | 0 | 1
# 0 | 1 | 1
# 1 | 0 | 1
# 1 | 1 | 1
class GenerateContext:
    def __init__(self, varnames):
        self.varnames = varnames
        self.n = len(self.varnames)
        # Generate the list of combinations (each row is a tuple)
        self.combinations = list(itertools.product([False, True], repeat=self.n))

    def evaluate_ast_row(self):
        # Loop through tuples of combinations
        for tuples in self.combinations:
            context = {}
            # Loop through elements of tuples
            for elements in tuples:
                # Get the variables from self.varnames set
                for variable in self.varnames:
                    context[variable] = elements

            # Run the parser on current dictionary of variables
            print(ast.evaluate(context))
            print(context)
        print(self.combinations)

parser = Parser(text="A.B")
ast = parser.parse()
#context = {'A': 0, 'B': 1, 'C': 1}
#print(ast.evaluate(context))
#print(parser.variables)
context = GenerateContext(parser.variables)
context.evaluate_ast_row()