"""
braintease.py

generates code for a brainfuck to gnu ia32 assembly compiler.
The generated code is then printed to stdout.

Rough overview of this approach:

    Treat brainfuck's single pointer as a pointer to top of stack.
    The stack grows to the right.

    All functions implemented below return strings which are
    strings of brainfuck opcodes, apart from compiler, which
    prints the complete program to stdout.

    Functions define words that operate on the stack.
    The little diagrams above the word definitions denote
    what the word does to the stack, in the form

        BEFORE STATE -> AFTER STATE
    
    The symbol ^ is used to denote the location of the
    stack pointer in the before and after states. Some
    of the operations have side effects.

    Each state is represented by a diagram made out of
    cells, e.g. '(x)(y)(z)'. If the cell contents is '.'
    then this means 'an arbitrary value'. single
    character contents e.g. 'x', 'y', 'z' denote
    named arbitrary values, to indicate how these
    values are transformed in the state after
    applying the word to the stack.
"""

# import strings assembly to emit for the
# various brainfuck opcodes
from compile import (
    READ_CHAR,
    WRITE_CHAR,
    PROGRAM_START,
    PROGRAM_END,
    DP_INC,
    DP_DEC,
    DP_LEFT,
    DP_RIGHT,
    BEGIN_WHILE,
    END_WHILE,
)

# insert this string into generated bf
# opcodes to trigger display of debugging
# info when program is interpreted with
# the brainfuck interpreter
from bf_interp import DEBUG_CHAR


#	(x) --> (0)
#	 ^       ^
def clear():
    return '[-]'


#   (x) --> (c)
#    ^       ^
#   where c is character from stdin (or 0 if EOF)
#   nb no way to distinguish receiving a 0 via
#   stdin from an EOF
#
#   side effects:
#       reads a character from stdin
def getchar():
    return clear() + ','


#   for gap = 0 (the default):
#
#	(x)(.)	-> (x)(x)
#	 ^	       ^
#   for gap > 0:
#
#       (x)(*)...(*)(.) -> (x)(*)...(*)(x)
#        ^                              ^
#   where gap (*) cells are skipped in between
#   the source and destination cells. the skipped
#   cells are NOT modified
def dupe(gap = 0):
    left_stride = '<' * gap
    right_stride = '>' * gap
    init = right_stride + '>' + clear() + '>' + clear() + '<<' + left_stride
    move_and_duplicate = '[-' + right_stride + '>+>+<<' + left_stride + ']'
    restore_source = right_stride + '>>[-<<' + left_stride + '+' + right_stride + '>>]<'
    return init + move_and_duplicate + restore_source


#   (x) -> (0 if x else 1)
#    ^          ^
def logical_not():
    return dupe() + '[<' + clear() + '->' + clear() + ']<+'


#   (x) -> (1 if x == c else 0)
#    ^      ^
def match_char(c):
    n = ord(c)
    return ('-' * n) + logical_not()


#   (.)(.) -> (.)(0)
#    ^         ^
#   side effects:
#       writes the given string to stdout.
#       the string is encoded into brainfuck opcodes
#       so we don't need to deal with the hassle of
#       storing it anywhere. this operation needs
#       1 cell of working memeory - it uses the cell
#       to the right of hte current stack pointer.
#       the contents of this cell are clobbered.
def put_string(s):
    # -- XXX note hideously verbose translation to brainfuck code
    #   to print each character c we execute a stream of
    #   2 * ord(c) + 1 brainfuck instructions
    # -- TODO improve this. obvious improvement would be
    #   to track the current value of the cell and
    #   to move directly to the next output value
    #   via the shortest sequence of - or + ops
    #   instead of always returning to 0
    body = [('+' * ord(c)) + '.' + ('-' * ord(c)) for c in s]
    return '>' + clear() + ''.join(body) + '<'


# (x)(.) -> (x)
#  ^         ^
# side effects:
#   executes action if x == c
def case(c, action):
    return dupe() + match_char(c) + '[' + action + clear() + ']<'


# special case statements to handle the '[' and ']' characters.
# in particular, we need to:
#   keep track of the next unique label index to use when beginning a while
#   keep track of the label index to use if ending a while loop
#
#   i think using a stack is the cleanest way to do this
#
#   e.g. perhaps the following convention
#
#   ie the format of each frame is
#   (n)(m)(c)
#          ^
#   where
#       n : next free unique index for label
#       m : innermost active index for label
#       c : the current character being translated


# (.)(x) -> (.)(0)
#     ^      ^
def put_label(prefix):
    # XXX TODO encode in less awful fashion than sequence of Ws
    return put_string(prefix) + '[' + put_string('W') + '-]<'


# (m)(n)(c)(1) --> (m)(n)(c)(m + 1)(m)(0)(1)
#           ^                             ^
# side effects:
#   emit code to begin while loop using
#   labels based on value of m
def begin_while():
    # assume BEGIN_WHILE has the form:
    #   foo <END_LABEL> barr <BEGIN_LABEL> bazz
    asm_code = BEGIN_WHILE
    asm_code = asm_code.replace('<END_LABEL>', '#')
    asm_code = asm_code.replace('<BEGIN_LABEL>', '#')
    asm_code = asm_code.split('#')
    assert len(asm_code) == 3
    
    return ''.join([
        '<<<', dupe(gap = 2), dupe(), '<+>',
        put_string(asm_code[0]),
        dupe(),
        put_label('end_'),
        put_string(asm_code[1]),
        dupe(),
        put_label('begin_'),
        put_string(asm_code[2]),
        '>',
        clear(),
        '>',
        clear(),
        '+',
    ])


# (x)(y)(z) -> (y)(0)(z)
#     ^         ^
def move_left():
    return '<' + clear() + '>[-<+>]<'


# (x)(y)(z)(m)(n)(c)(1) -> (m)(y)(0)(1)
#                    ^               ^
# side effects:
#   emit code to close loop corresponding
#   to the unique loop index y
def end_while():
    # assume END_WHILE has the form:
    #   foo <BEGIN_LABEL> barr <END_LABEL> bazz
    asm_code = END_WHILE
    asm_code = asm_code.replace('<END_LABEL>', '#')
    asm_code = asm_code.replace('<BEGIN_LABEL>', '#')
    asm_code = asm_code.split('#')
    assert len(asm_code) == 3
    return ''.join([
        clear(),
        '<',
        clear(),
        '<',
        put_string(asm_code[0]),
        dupe(),
        put_label('begin_'),
        put_string(asm_code[1]),
        put_label('end_'),
        put_string(asm_code[2]),
        # (x)(y)(z)(m)
        #           ^
        '<<',
        dupe(gap = 2),
        '<',
        move_left(), move_left(), move_left(),
        '>>>>',
        move_left(), move_left(), move_left(),
        '>>+',
        # (m)(z)(0)(1)
        #           ^
    ])


def compiler():
    """
    print opcodes for brainfuck compiler to stdout
    """
    fragments = (
        put_string(PROGRAM_START),
        clear(), '>', clear(), '>',
        getchar(),
        '[',
            case('+', put_string(DP_INC)),
            case('-', put_string(DP_DEC)),
            case('<', put_string(DP_LEFT)),
            case('>', put_string(DP_RIGHT)),
            case(',', put_string(READ_CHAR)),
            case('.', put_string(WRITE_CHAR)),
            case('[', begin_while()),
            case(']', end_while()),
            getchar(),
        ']',
        put_string(PROGRAM_END),
    )
    for s in fragments:
        print s

if __name__ == '__main__':
    compiler()
