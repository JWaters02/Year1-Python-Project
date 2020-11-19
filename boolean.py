#import PrettyTable

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

class Token:
    # Provides alternatives to each operator with possible inputted mathematical symbols
    TOKEN_ALTERNATIVES = {
        '!' : '!',
        'not' : '!',
        '¬' : '!',
        '-' : '!',
        '+' : '+',
        'or' : '+',
        '|' : '+',
        'v' : '+',
        '.' : '.',
        'and' : '.',
        '^' : '.',
        '&' : '.'
    }


# Evalutates not expressions
class NotExpression:
    def __init__(self, sub_expr):
        self.sub_expr = sub_expr

    def evaluate(self):
        return not self.sub_expr.evaluate()


# Evaluates and expressions
class AndExpression:
    def __init__(self, sub_expr_left, sub_expr_right):
        self.sub_expr_left = sub_expr_left
        self.sub_expr_right = sub_expr_right

    def evaluate(self):
        return self.sub_expr_left.evaluate() and self.sub_expr_right.evaluate()


# Evaluates or expressions
class OrExpression:
    def __init__(self, sub_expr_left, sub_expr_right):
        self.sub_expr_left = sub_expr_left
        self.sub_expr_right = sub_expr_right

    def evaluate(self):
        return self.sub_expr_left.evaluate() or self.sub_expr_right.evaluate()


# Evaluates parentheses in the expression
class ParenthesizedSymbol:
    def __init__(self, sub_expr):
        self.sub_expr = sub_expr
    
    def evaluate(self):
        return self.sub_expr.evaluate()


# Evaluates any variables in the expression 
class VariableSymbol:
    def __init__(self, letter):
        self.letter = letter
    
    def evaluate(self, context):
        return context[self.letter]


# Parses each section of the expression into a usable state
class Parser:
    def __init__(self, text):
        self.text = text.replace(' ', '') # Removes whitespace
        self.pos = 0
        self.variables = set()

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
    
    # Returns any varianles in the expression
    def parse_variable_symbol(self):
        name = self.consume_token()
        self.variables.add(name)
        return VariableSymbol(name)

    # 
    def parse_expression(self):
        terms = []
        terms.append(self.parse_term())
        token = self.consume_token()
        while token == Token.TOKEN_ALTERNATIVES['+']:
            terms.append(self.parse_term())
            token = self.consume_token()
        return terms

    # 
    def parse_term(self):
        terms = []
        terms.append(self.parse_term())
        token = self.consume_token()
        while token == Token.TOKEN_ALTERNATIVES['.']:
            terms.append(self.parse_term())
            token = self.consume_token()
        return terms

    # Errors if parentheses missing,
    # Returns the expression within the parentheses
    def parse_parenthesized_symbol(self):
        if self.consume_token() != '(':
            raise Exception('Incorrect syntax')
        ret = ParenthesizedSymbol(self.parse_expression())
        if self.consume_token() != ')':
            raise Exception('Incorrect syntax')
        return ret

    # Parsed expression
    def parse(self):
        ret = self.parse_expression()
        if self.consume_token() is not None:
            raise Exception('Parse error')
        return ret


parser = Parser(text="A + B")
ast = parser.parse()
# Iterate through context to get every part of it
context = {'a': False, 'b': True}