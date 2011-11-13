import sys

DEBUG_CHAR = '@'

def die(s):
    print
    print 'Error:'
    print s
    sys.exit(1)

class State:
    def __init__(self, n_cells, get_char, put_char):
        self.n_cells = n_cells
        self.buff = [0] * n_cells
        self.dp = 0
        self.get_char = get_char
        self.put_char = put_char

    def left(self):
        assert self.dp > 0
        self.dp -= 1

    def right(self):
        assert self.dp < (self.n_cells - 1)
        self.dp += 1

    def inc(self):
        self.buff[self.dp] = (self.buff[self.dp] + 1) % 256

    def dec(self):
        self.buff[self.dp] = (self.buff[self.dp] - 1) % 256

    def read(self):
        self.buff[self.dp] = self.get_char()

    def write(self):
        self.put_char(self.buff[self.dp])

    def cell_zero(self):
        return (self.buff[self.dp] == 0)

def advance_to_matching_right_brace(program, pc):
    level = 0
    pc_end = len(program)
    while 0 <= pc < pc_end:
        c = program[pc]
        if c == '[':
            level += 1
        if c == ']':
            level -= 1
            if level == 0:
                return pc
        pc += 1
    die('unmatched [')

def rewind_to_matching_left_brace(program, pc):
    level = 0
    pc_end = len(program)
    while 0 <= pc < pc_end:
        c = program[pc]
        if c == '[':
            level -= 1
            if level == 0:
                return pc
        if c == ']':
            level += 1
        pc -= 1
    die('unmatched ]  (???)')

def dbg_display_state(state, pc):
    print '# DBG'
    print '# pc = %d, dp = %d' % (pc, state.dp)
    fmt_cell = lambda x : '[% 3d]' % x
    n_cells = 16
    print '# %s' % ''.join(map(fmt_cell, state.buff[:n_cells]))
    if state.dp < 16:
        print '# ' + (('     ' * state.dp) + '^^^^^')

def interp(state, program, debug = False):
    pc = 0
    pc_end = len(program)
    steps = 0
    while (pc < pc_end):
        c = program[pc]
        if c == '+':
            state.inc()
        elif c == '-':
            state.dec()
        elif c == '>':
            state.right()
        elif c == '<':
            state.left()
        elif c == '.':
            state.write()
        elif c == ',':
            state.read()
        elif c == '[':
            if state.cell_zero():
                pc = advance_to_matching_right_brace(program, pc)
        elif c == ']':
            if not state.cell_zero():
                pc = rewind_to_matching_left_brace(program, pc)
        elif c == DEBUG_CHAR and debug:
            dbg_display_state(state, pc)
        pc += 1
        steps += 1

def main():

    def put_char(x):
        sys.stdout.write(chr(x))
        sys.stdout.flush()
    
    def get_char():
        c = sys.stdin.read(1)
        if len(c) == 0:
            return 0
        else:
            return ord(c)
    
    n_cells = 30000
    state = State(n_cells, get_char, put_char)

    with open(sys.argv[1], 'r') as program_f:
        program = '\n'.join(program_f.readlines())

    interp(state, program, debug = True)

if __name__ == '__main__':
    main()
