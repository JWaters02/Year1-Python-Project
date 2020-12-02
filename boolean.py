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
        self.text = text
        self.pos = 0
        self.variableSet = set() # Tracks all the variables in the expression
        self.variables = []
        self.NOT_ALTERNATIVES = [
            '!', 'not', '¬', '-'
        ]
        self.OR_ALTERNATIVES = [
            '+', 'or', '|', 'v'
        ]
        self.AND_ALTERNATIVES = [
            '.', 'and', '^', '&'
        ]

    def order_variable_set(self):
        return sorted(self.variableSet)

    # Reads the tokens of the expression by iterating through the position
    def consume_token(self):
        # Skips over whitespace
        while self.pos < len(self.text) and self.text[self.pos] == ' ':
            self.pos += 1
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
        self.variables = self.order_variable_set()
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
        self.variableSet.add(name)
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
    def __init__(self, variables):
        self.variables = variables
        self.numVars = len(self.variables)
        # Generate the list of combinations (each row is a tuple)
        self.combinations = list(itertools.product([0, 1], repeat=self.numVars))

    def evaluate_ast_row(self):
        contextRow = {}
        context = []
        # Loop through tuples of combinations
        for tuples in self.combinations:
            # Loop through elements of tuples
            contextRow = (dict(zip(self.variables, tuples)))
            # Add the dictionary (row) to the list of dicts (rows)
            context.append(contextRow)
        return context

    def generate_truths(self):
        context = self.evaluate_ast_row()
        outputRow = []
        for row in context:
            # Run the parser on current dictionary of variables
            outputRow.append(dict(ast.evaluate(context[row])))
        return outputRow


class QM:
    def __init__(self, context, outputRow):
        self.context = context
        self.outputRow = outputRow
        self.minterms = []

    def generate_min_terms(self):
        for row in self.context:
            # Turn the corresponding context row into decimal
            self.minterms.append(int(self.context[row]))
        print(self.minterms)
        
    def group_terms(self):
        groups = [[[]]]
        numOfGroupSets = (len(self.context[0]) + 1) # Num of group SETS is decided by number of bits + 1
        self.remove_dont_cares()
        
        for row in self.context:
            # =====================================
            # FIRST SET OF GROUPS
            # The group number is decided by the number of 1s in the row (want to start from 0)
            groupNumber = (len(self.context[row].count(1)) - 1)
            groups[0][groupNumber][row].append(self.minterms[row])
            numberOfGroups = len(groups[0][groupNumber][row])

        # Get the number of sets of groups that need to be generated
        for groupSet in range(numOfGroupSets):
            for row in range(groupNumber):
                # =====================================
                # SECOND SET OF GROUP SETS
                # Any adjacent set which has a context row that is only one value different, add that to corresponding group
                # E.g. min terms 2,6 are 1 off and in adjacent groups, put them in one group together, in one ROW

                # Use itertools.product() to generate all the combinations of the adjacent groups
                # Makes sure groups loop over to the next group if checking from last group
                if (groupNumber - 1) < 0:
                    adjacentTerms = list(itertools.product(groups[groupSet][numberOfGroups - groupNumber][row], groups[groupSet][groupNumber][row]))
                else:
                    adjacentTerms = list(itertools.product(groups[groupSet][groupNumber - 1][row], groups[groupSet][groupNumber][row]))
                    
                for i in adjacentTerms:
                    # If current term is only one off, binary-wise, to the next term
                    # Replace that bit with a '-'
                    if (adjacentTerms - 1) < 0:
                        if self.does_bit_differ_by_one(self.context[i], self.context[i + 1]):
                            #TODO: Need to set both the minterms of new groupset, groupnumber row AND new bin number of row
                            groups[groupSet][groupNumber][row] = str(self.minterms[groupNumber], self.minterms[groupNumber])
                    

    def remove_dont_cares(self):
        # Loop through table rows
        for row in self.context:
            if self.outputRow[row] == 0:
                # Remove that row from context, outputRow and minterms lists
                self.outputRow[row].Remove(row)
                self.context[row].Remove(row)
                self.minterms[row].Remove(row)

    def does_bit_differ_by_one(self, firstByte, secondByte):
        # Uses bitwise XOR
        # diff = firstByte ^ secondByte
        # return diff and (not(diff & (diff - 1)))
        count_diffs = 0
        for a, b in zip(firstByte, secondByte):
            if a != b:
                count_diffs += 1
        if count_diffs == 1: return True
        else: return False

    def modify_bit(self, firstByte):
        # # Uses bitwise XOR
        # diff = firstByte ^ secondByte
        # # Gets pos of diff bit (right to left)
        # pos = diff.bit_length() - 1
        # strFByte = str(firstByte)
        # newByte = strFByte[pos].replace(strFByte[pos], '-')
        # return newByte
        # String slicing
        pos=2
        return str(firstByte)[:pos] + '-' + str(firstByte)[pos + 1:]



parser = Parser(text="(A and B)+C")
ast = parser.parse()
#context = {'A': 0, 'B': 1, 'C': 1}
context = GenerateContext(parser.variables)
outputRows = context.generate_truths()
print(outputRows)