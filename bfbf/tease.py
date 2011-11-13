"""
sketch of brainfuck compiler in brainfuck
"""

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

from bf_interp import DEBUG_CHAR

#	(x) --> (0)
#	 ^       ^
def clear():
    return '[-]'

#   (x) --> (c)
#    ^       ^
#   where c is character from stdin (or 0 if EOF)
#   nb no way to distinguish 0 in file from EOF
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

#   (.) -> (.)
#    ^      ^
def put_string(s):
    # -- TODO improve this. obvious improvement would be
    #   to track the current value of the cell and
    #   to move directly to the next output value
    #   via the shortest sequence of - or + ops
    #   instead of always returning to 0

    # note hideously verbose translation to brainfuck code
    # -- to print each character c we execute a stream of
    # 2 * ord(c) + 1 brainfuck instructions, not using
    # any loops
    body = [('+' * ord(c)) + '.' + ('-' * ord(c)) for c in s]
    return '>' + clear() + ''.join(body) + '<'

# (x)(.) -> (x)
#  ^         ^
# side effects:
#   executes action if x == c
def case(c, action):
    return dupe() + match_char(c) + '[' + action + clear() + ']<'

# todo:
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
#
#   two stack transformations need to be implemented:
#
#   (n)(m)('[') --> (n)(m)(c)(n + 1)(n)(ignored_char)
#          ^                            ^
#   (n)(m)(c)(o)(p)(']') --> (o)(m)(ignored_char)
#                    ^              ^
#   here, ignored_char is any constant value that
#   is not recognised as a character and parsed
#   i.e., it is not one of the 8 brainfuck operations,
#   AND IT IS ALSO NOT THE END OF FILE VALUE 0
#
#   each stack transformation also needs a side effect
#   of emitting the correct code (using n to define
#   labels on '[', and p to define labels on ']')
#
#   basically it would be sufficient to implement
#   a routine that does a duplicate, but places the
#   result 3 cells to the right, without touching
#   clobbering the two cells in between (or indeed
#   the leftmost 'source' cell), ie want
#
#   (a)(b)(c)(.)   ->  (a)(b)(c)(a)
#             ^                  ^
#   XXX: this is now implemented as a generalised dupe(gap = 3)
#   stack operator

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
