import itertools
import time


# ======================
# Backus-Naur Form

# <expression> ::= <term> ( <or_symbol> <term> )...
# <or_symbol> ::= "+" | "or"
# <term> ::= <symbol> ( ("." | "and") <symbol> )...
# <symbol> ::= <not_symbol> | <parenthesized_symbol> | <variable> | <literal>
# <not_symbol> ::= "!" <symbol>
# <parenthesized_symbol> ::= "(" <expression> ")"
# <variable> ::= a letter
# <literal> ::= "0" | "1"

# ====================== 


# Evaluates not symbols
class NotExpression:
    def __init__(self, sub_symbol):
        self.sub_symbol = sub_symbol

    def evaluate(self, _context):
        return not self.sub_symbol.evaluate(_context)


# Evaluates and terms
class AndExpression:
    def __init__(self, and_list):
        self.and_list = and_list

    def evaluate(self, _context):
        for term in self.and_list:
            if not term.evaluate(_context):
                return False
        return True


# Evaluates or expressions
class OrExpression:
    def __init__(self, expression_list):
        self.expression_list = expression_list

    def evaluate(self, _context):
        for expr in self.expression_list:
            if expr.evaluate(_context):
                return True
        return False


# Evaluates parentheses in the expression
class ParenthesizedSymbol:
    def __init__(self, sub_expr):
        self.sub_expr = sub_expr

    def evaluate(self, _context):
        return self.sub_expr.evaluate(_context)


# Evaluates any variables
class VariableSymbol:
    def __init__(self, letter):
        self.letter = letter

    def evaluate(self, _context):
        return _context[self.letter]


# Evaluates any literals
class LiteralSymbol:
    def __init__(self, literal):
        self.literal = literal

    def evaluate(self, _context):
        return self.literal


# Parses each section of the expression into a usable state
class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.variableSet = set()  # Tracks all the variables in the expression
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
            return None  # None = special token
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
        prev_pos = self.pos
        ret = self.consume_token()
        self.pos = prev_pos
        return ret

    # Parsed expression
    def parse(self):
        ret = self.parse_or()
        if self.consume_token() is not None:
            raise Exception('Error: Parse error')
        self.variables = self.order_variable_set()
        return ret

    # Returns the or of expression
    def parse_or(self):
        terms = [self.parse_and()]
        token = self.peek_token()
        while token in self.OR_ALTERNATIVES:
            token = self.consume_token()
            terms.append(self.parse_and())
            token = self.peek_token()
        ret = OrExpression(terms)
        return ret

    # Returns the and term of expression
    def parse_and(self):
        terms = [self.parse_symbol()]
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
        if token not in self.NOT_ALTERNATIVES:
            raise Exception('Error: Invalid syntax')
        sub_symbol = self.parse_symbol()
        ret = NotExpression(sub_symbol)
        return ret

    # Returns the expression within the parentheses
    # Errors if either parentheses missing
    def parse_parenthesized_symbol(self):
        token = self.consume_token()
        if not token == "(":
            raise Exception('Error: Missing (')
        ret = ParenthesizedSymbol(self.parse_or())
        token = self.consume_token()
        if not token == ")":
            raise Exception('Error: Missing )')
        return ret

    # Returns any variables in the expression/term
    # Raises an error if the variable is not text
    def parse_variable_symbol(self):
        name = self.consume_token()
        if name is None:
            raise Exception('Error: variable not detected')
        if not name.isalpha():
            raise Exception('Error: variable not detected')
        self.variableSet.add(name)
        return VariableSymbol(name)

    # Returns if literal is true or false
    def parse_literal(self):
        token = self.consume_token()
        if not token == "1" and not token == "0":
            raise Exception('Error: Incorrect syntax')
        if token == "1":
            literal = True
        else:
            literal = False
        ret = LiteralSymbol(literal)
        return ret


# Generates all the combinations of the truth table based on the variables given
class GenerateContext:
    def __init__(self, variables):
        self.variables = variables
        num_vars = len(self.variables)
        # Generate the list of combinations (each row is a tuple)
        self.combinations = list(itertools.product([0, 1], repeat=num_vars))

    def evaluate_ast_row(self):
        _context = []
        # Loop through tuples of combinations
        for tuples in self.combinations:
            # Loop through elements of tuples
            context_row = (dict(zip(self.variables, tuples)))
            # Add the dictionary (row) to the list of dicts (rows)
            _context.append(context_row)
        return _context

    def generate_truths(self):
        _context = self.evaluate_ast_row()
        output_row = []
        for row in _context:
            # Run the parser on current dictionary of variables
            output_row.append(ast.evaluate(row))
        return output_row


# Runs the Quine-McClusky algorithm and further simplifies using Petrick's method
class QM:
    def __init__(self, _context, _outputRow, variables):
        self.context = _context
        self.output_row = _outputRow
        self.variables = variables
        self.minterms = []
        self.prime_implicants = set()
        self.function = []

    # Generates binary minterms from context
    def generate_min_terms(self):
        for row in self.context:
            # Turn the corresponding context row into decimal
            minterm = ''
            for element in row:
                minterm += str(row.get(element))
            self.minterms.append(int(minterm, 2))

    # Removes all minterms that have output of 0
    def remove_dont_cares(self):
        # Loop through table rows
        pos_flags = []
        temp = []
        i = 0
        for pos, row in enumerate(self.output_row):
            if not row:
                temp.append(self.output_row[row])
            else:
                pos_flags.append(pos)
        self.output_row = temp.copy()

        for pos in pos_flags:
            self.minterms.pop(pos - i)
            i += 1

    # Flattens a list
    def list_flatten(self, input_list):
        flattened_elements = []
        for i in input_list:
            flattened_elements.extend(input_list[i])
        return flattened_elements

    # Finds out which minterms have been merged
    # E.g. -100 is gotten by merging 1100 and 0100
    def find_merged_minterms(self, minterm):
        differed_bit = minterm.count('-')
        # If minterms not been merged
        if differed_bit == 0:
            return [str(int(minterm, 2))]
        diff = [bin(i)[2:].zfill(differed_bit) for i in range(pow(2, differed_bit))]
        temp_list = []
        # Iterate through number of bits changed to '-'
        for x in range(pow(2, differed_bit)):
            temp_min_terms = minterm[:]
            prev_term = -1
            # Iterate through bin number with differed bits in empty slots
            for y in diff[0]:
                if prev_term != -1:
                    prev_term = prev_term + temp_min_terms[prev_term + 1:].find('-') + 1
                else:
                    prev_term = temp_min_terms[prev_term + 1:].find('-')
                temp_min_terms = temp_min_terms[:prev_term] + y + temp_min_terms[prev_term + 1:]
            temp_list.append(str(int(temp_min_terms, 2)))
            diff.pop(0)
        return temp_list

    # Creates the prime implicants list from the minterms which have been merged
    def generate_prime_implicants(self):
        prime_implicants_list = {}
        for i in self.prime_implicants:
            # List of minterms that have been merged
            merged_minterms = self.find_merged_minterms(i)
            for j in merged_minterms:
                try:
                    # Add prime implicants to list
                    if i not in prime_implicants_list[j]:
                        prime_implicants_list[j].append(i)
                    else:
                        pass
                except KeyError:
                    prime_implicants_list[j] = [i]
        return prime_implicants_list

    # Finds all essential prime implicants in the prime implicants list
    def generate_essential_prime_implicants(self, prime_implicants):
        ret = []
        for i in prime_implicants:
            if len(prime_implicants[i]) == 1:
                if prime_implicants[i][0] not in ret:
                    ret.append(prime_implicants[i][0])
                else:
                    None
        return ret

    # Finds variables from minterm
    # E.g. minterm -10- (assuming vars a, b, c, d) would be BC'
    def generate_variables_from_minterm(self, minterm):
        ret = []
        for i in range(len(minterm)):
            current_var = self.variables[i]
            if minterm[i] == '0':
                ret.append(current_var + "'")
            elif minterm[i] == '1':
                ret.append(current_var)
        return ret

    # Returns true or false on comparison and position of differ (if true)
    def does_bit_differ_by_one(self, first_bin_num, second_bin_num):
        diff_pos = 0
        count_diffs = 0
        for i in range(len(first_bin_num)):
            if first_bin_num[i] != second_bin_num[i]:
                diff_pos = i
                count_diffs += 1
                if count_diffs > 1:
                    return False, None
        if count_diffs == 0:
            return False, None
        return True, diff_pos

    # Multiplies 2 minterms
    def multiply_minterms(self, exp1, exp2):
        ret = []
        for x in exp1:
            # Checks with the ' in the place
            if x + "'" in exp2 or (len(x) == 2 and x[0] in exp2):
                return []
            else:
                ret.append(x)
        for x in exp2:
            if x not in ret:
                ret.append(x)
        return ret

    # Multiplies 2 expressions
    def multiply_expressions(self, exp1, exp2):
        ret = []
        for x in exp1:
            for y in exp2:
                multi_exp = self.multiply_minterms(x, y)
                ret.append(multi_exp) if len(multi_exp) != 0 else None
        return ret

    # Generates groups for all terms
    def group_terms(self):
        self.generate_min_terms()
        self.remove_dont_cares()
        self.minterms.sort()
        bin_length = len(bin(self.minterms[-1])) - 2
        groups = {}

        # FIRST SET OF GROUPS
        # The group number is decided by the number of 1s in the row (want to start from 0)
        # Groups dict: Key is number of 1s in minterm, content is all the minterms with that number of 1s
        for term in self.minterms:
            num_ones_in_minterm = (bin(term).count('1'))
            try:
                # If group exists,
                # Append current minterm to correct group dict list (according to key)
                groups[num_ones_in_minterm].append((bin(term)[2:].zfill(bin_length)))
            except KeyError:
                # If group does not already exist,
                # Set current minterm to new group dict list (according to key)
                groups[num_ones_in_minterm] = [(bin(term)[2:].zfill(bin_length))]

        # SECOND SET OF GROUP SETS
        # Any adjacent set which has a context row that is only one value different, add that to corresponding group
        # E.g. min terms 2,6 are 1 off and in adjacent groups, put them in one group together
        # And finds prime implicants
        while True:
            first_set_groups = groups.copy()
            break_loop = True
            changed_minterms = set()
            group_num = 0
            groups = {}
            group_elements = sorted(list(first_set_groups.keys()))
            for x in range(len(group_elements) - 1):
                # Iterates current group elements
                for y in first_set_groups[group_elements[x]]:
                    # Iterates next group elements
                    for z in first_set_groups[group_elements[x + 1]]:
                        bit_differ = self.does_bit_differ_by_one(y, z)
                        # If minterms differ by one bit
                        if bit_differ[0]:
                            try:
                                # If group set already exists
                                if y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:] not in groups[group_num]:
                                    # Replace the different bit in diff pos with a '-'
                                    groups[group_num].append(y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:])
                                else:
                                    pass
                            except KeyError:
                                # If group set does not exist, create the group set
                                groups[group_num] = [y[:bit_differ[1]] + '-' + y[bit_differ[1] + 1:]]
                            break_loop = False
                            changed_minterms.add(y)
                            changed_minterms.add(z)
                group_num += 1

            # Stores all the unchanged minterms
            unchanged_minterms = set(self.list_flatten(first_set_groups)).difference(changed_minterms)
            # Add any minterms that can't go further, to prime implicants set
            self.prime_implicants = self.prime_implicants.union(unchanged_minterms)

            # If the minterms can't be combined further
            if break_loop:
                break

    # Petrick's method determines all the minimum SOP (sum of product) solutions from the prime implicants list
    def petricks_method(self, _prime_implicants_list, _essential_prime_implicants):
        petrick = [[self.generate_variables_from_minterm(x) for x in _prime_implicants_list[y]] for y in
                   _prime_implicants_list]
        # Multiplies terms until sum of products of term is reached
        while len(petrick) > 1:
            petrick[1] = self.multiply_expressions(petrick[0], petrick[1])
            petrick.pop(0)
        # Chooses the term with the least variables
        self.function = [min(petrick[0], key=len)]
        # Adds the essential prime implicants to final function
        self.function.extend(self.generate_variables_from_minterm(i) for i in _essential_prime_implicants)

    def generate_solution(self):
        self.group_terms()
        prime_implicants_list = self.generate_prime_implicants()
        # Finds the essential prime implicants from prime implicants list
        essential_prime_implicants = self.generate_essential_prime_implicants(prime_implicants_list)
        # Removes all the essential prime implicants from primeimplicants list
        for x in essential_prime_implicants:
            for y in self.find_merged_minterms(x):
                try:
                    del prime_implicants_list[y]
                except KeyError:
                    pass

        # If no minterms are left after removing all the essential prime implicants
        if len(prime_implicants_list) == 0:
            # Set the function
            self.function = [self.generate_variables_from_minterm(i) for i in essential_prime_implicants]
        # If there are left, use Petrick's method to simplify further
        else:
            self.petricks_method(prime_implicants_list, essential_prime_implicants)

        # If there is no function
        if not any(self.function):
            print('There is no solution to this expression.')
        else:
            print('Solution: F = ' + ' + '.join(''.join(i) for i in self.function))


# Loop expression inputs until the user chooses to quit
while True:
    print(
        "Boolean expression simplifier. Input your expression below or type 'quit' to quit. Supported tokens "
        "are:\n'!', 'not', '¬', '-',\n'+', 'or', '|', 'v',\n'.', 'and', '^', '&'.\nE.g. '(A and B) or C' is "
        "equivalent to '(A.B) + C'")
    expression = input()
    if expression.lower() == "quit":
        break
    else:
        start = time.time()
        print("================================")
        parser = Parser(expression)
        ast = parser.parse()
        genContext = GenerateContext(parser.variables)
        outputRows = genContext.generate_truths()
        context = genContext.evaluate_ast_row()
        mcclusky = QM(context, outputRows, parser.variables)
        mcclusky.generate_solution()
        end = time.time()
        print(f"Overall execution time: {end - start}")
        print("================================")
