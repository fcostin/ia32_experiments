"""
brainfuck -> gnu ia32 assembly compiler.
"""

import sys
import itertools
from ia32 import *

def die(s):
    print s
    sys.exit(1)

def emit(s):
    print s

def compile(s):
    unique_labels = itertools.count()
    label_stack = []

    def begin_while():
        i = unique_labels.next()
        label_stack.append(i)
        return (BEGIN_WHILE_1 + ('end_%d' % i) +
            BEGIN_WHILE_2 + ('begin_%d' % i) +
            BEGIN_WHILE_3)

    def end_while():
        if not label_stack:
            die('error: encountered "]" without matching "["')
        i = label_stack.pop()
        return (END_WHILE_1 + ('begin_%d' % i) +
            END_WHILE_2 + ('end_%d' % i) +
            END_WHILE_3)

    code_generator = {
        '<' : lambda : DP_LEFT,
        '>' : lambda : DP_RIGHT,
        '+' : lambda : DP_INC,
        '-' : lambda : DP_DEC,
        '[' : begin_while,
        ']' : end_while,
        '.' : lambda : WRITE_CHAR,
        ',' : lambda : READ_CHAR,
    }
    emit(PROGRAM_START)
    for c in s:
        if c in code_generator:
            emit(code_generator[c]())
        else:
            pass # ignore unrecognised characters
    emit(PROGRAM_END)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as source_file:
        s = '\n'.join(source_file.readlines())
    compile(s)
