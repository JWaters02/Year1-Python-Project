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


class GenerateContext:
    def __init__(self, variables):
        self.variables = variables
        numVars = len(self.variables)
        # Generate the list of combinations (each row is a tuple)
        self.combinations = list(itertools.product([0, 1], repeat=numVars))

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
            outputRow.append(ast.evaluate(row))
        return outputRow


class QM:
    def __init__(self, context, outputRow, variables):
        self.context = context
        self.outputRow = outputRow
        self.variables = variables
        self.minterms = []
        self.prime_implicants = set()

    # Generates binary minterms from context
    def generate_min_terms(self):
        for row in self.context:
            # Turn the corresponding context row into decimal
            minterm = ''
            for element in row:
                minterm += str(row.get(element))
            self.minterms.append(int(minterm, 2))
        print(self.minterms)
        
    # Removes all minterms that have output of 0
    def remove_dont_cares(self):
        # Loop through table rows
        for row in self.context:
            if self.outputRow[row] == 0:
                # Remove that row from context, outputRow and minterms lists
                self.outputRow[row].Remove(row)
                self.context[row].Remove(row)
                self.minterms[row].Remove(row)

    # Flattens a list
    def list_flatten(self, inputList):
        flattened_elements = []
        for i in inputList:
            flattened_elements.extend(inputList[i])
        return flattened_elements

    # Finds out which minterms have been merged
    # E.g. -100 is gotten by merging 1100 and 0100
    def find_merged_minterms(self, minterm):
        differedBit = minterm.count('-')
        # If minterms not been merged
        if differedBit == 0:
            return [str(int(minterm, 2))]
        diff = [bin(i)[2:].zfill(differedBit) for i in range(pow(2, differedBit))]
        tempList = []
        # Iterate through number of bits changed to '-'
        for x in range(pow(2, differedBit)):
            tempMinTerms = minterm[:]
            prevTerm = -1
            # Iterate through bin number with differed bits in empty slots
            for y in diff[0]:
                if prevTerm != -1:
                    prevTerm = prevTerm + tempMinTerms[prevTerm + 1:].find('-') + 1
                else:
                    prevTerm = tempMinTerms[prevTerm + 1:].find('-')
                tempMinTerms = tempMinTerms[:prevTerm] + y + tempMinTerms[prevTerm + 1:]
            tempList.append(str(int(tempMinTerms, 2)))
            diff.pop(0)
        return tempList

    # Finds all essential prime implicants in the prime implicants list
    def generate_essential_prime_implicants(self, primeImplicants):
        ret = []
        for i in primeImplicants:
            if len(primeImplicants[i]) == 1:
                if primeImplicants[i][0] not in ret:
                    ret.append(primeImplicants[i][0])
                else:
                    None
        return ret

    # Finds variables from minterm
    # E.g. minterm -10- (assuming vars a, b, c, d) would be BC'
    def generate_variables_from_minterm(self, minterm):
        ret = []
        for i in range(len(minterm)):
            currentVar = self.variables[i]
            if minterm[i] == '0':
                ret.append(chr(currentVar) + "'")
            elif minterm[i] == '1':
                ret.append(chr(currentVar))
        return ret

    # Returns true or false on comparison and position of differ (if true)
    def does_bit_differ_by_one(self, firstBinNum, secondBinNum):
        diffPos = 0
        count_diffs = 0
        for i in range(len(firstBinNum)):
            if firstBinNum[i] != secondBinNum[i]:
                diffPos = i
                count_diffs += 1
                if count_diffs > 1:
                    return False, None
        return True, diffPos
    
    def group_terms(self):
        self.generate_min_terms()
        self.minterms.sort()
        binLength = len(bin(self.minterms[-1])) - 2
        print(binLength)
        groups = {}

        # FIRST SET OF GROUPS
        # The group number is decided by the number of 1s in the row (want to start from 0)
        # Groups dict: Key is number of 1s in minterm, content is all the minterms with that number of 1s
        for term in self.minterms:
            numOnesInMinterm = (bin(term).count('1'))
            try:
                # If group exists,
                # Append current minterm to correct group dict list (according to key)
                groups[numOnesInMinterm].append((bin(term)[2:].zfill(binLength)))
            except KeyError:
                # If group does not already exist,
                # Set current minterm to new group dict list (according to key)
                groups[numOnesInMinterm] = [(bin(term)[2:].zfill(binLength))]
        print(groups)

        # SECOND SET OF GROUP SETS
        # Any adjacent set which has a context row that is only one value different, add that to corresponding group
        # E.g. min terms 2,6 are 1 off and in adjacent groups, put them in one group together
        # And finds prime implicants
        while True:
            firstSetGroups = groups.copy()
            breakLoop = True
            changedMinterms = set()
            groupNum = 0
            secondSetGroupsSets = {}
            groupElements = sorted(list(firstSetGroups.keys()))
            for x in range(len(groupElements) - 1):
                # Iterates current group elements
                for y in firstSetGroups[groupElements[x]]:
                    # Iterates next group elements
                    for z in firstSetGroups[groupElements[x + 1]]:
                        bit_differ = self.does_bit_differ_by_one(y, z)
                        # If minterms differ by one bit
                        if bit_differ[0]:
                            try:
                                # If group set already exists
                                if y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:] not in secondSetGroupsSets[groupNum]:
                                    # Replace the different bit in diff pos with a '-'
                                    secondSetGroupsSets[groupNum].append(y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:])
                                else:
                                    None
                            except KeyError:
                                # If group set does not exist, create the group set
                                secondSetGroupsSets[groupNum] = [y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:]]
                            breakLoop = False
                            changedMinterms.add(y)
                            changedMinterms.add(z)
                groupNum += 1

            # Stores all the unchanged minterms
            unchangedMinterms = set(self.list_flatten(firstSetGroups)).difference(changedMinterms)
            # Add any minterms that can't go further, to prime implicants set
            self.prime_implicants = self.prime_implicants.union(unchangedMinterms)
            print("Unmarked elements: ", None if len(unchangedMinterms) == 0 else ', '.join(unchangedMinterms))
            # If the minterms can't be combined further
            if breakLoop:
                break

        primeImplicantsList = {}
        for i in self.prime_implicants:
            for j in self.minterms:
                try:
                    # Add prime implicants to list
                    if i not in primeImplicantsList[j]:
                        primeImplicantsList[j].append(i)
                    else:
                        None
                except KeyError:
                    primeImplicantsList[j] = [i]

        essentialPrimeImplicants = self.generate_essential_prime_implicants(primeImplicantsList)
        print(essentialPrimeImplicants) # TODO: Further simplification using Petrick's method?


parser = Parser(text="(A . B)+C")
ast = parser.parse()
#context = {'A': 0, 'B': 1, 'C': 1}
#print(ast.evaluate(context))
genContext = GenerateContext(parser.variables)
outputRows = genContext.generate_truths()
context = genContext.evaluate_ast_row()
print(outputRows)
mcclusky = QM(context, outputRows, parser.variables)
mcclusky.group_terms()