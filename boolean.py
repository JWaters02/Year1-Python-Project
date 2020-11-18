#import PrettyTable

class Expression:
    # Defines each of the operators
    OPERATORS = {
        '!' : lambda x: str(int(not int(x))),
        '+' : lambda x, y : str(int(int(x) or int(y))),
        '.' : lambda x, y : str(int(int(x) and int(y)))
    }

    # Provides alternatives to each operator with possible inputted mathematical symbols
    OPERATOR_ALTERNATIVES = {
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

    # Forces the algebraic order of each operator
    OPERATOR_ORDER = {
        '!' : 2,
        '.' : 1,
        '+' : 0
    }