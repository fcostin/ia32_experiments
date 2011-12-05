"""
HAHAHAHAHAHAHA

    wtf #1:
        at the moment, _invoke_macro(machine, 'foo', *args)
        does essentially the same thing as foo(machine, *args).
        i cannot think of a redeeming feature of this.

    pseudo-wtf #2:
        the endless lines of

            machine.do_foo()
            ...
            machine.do_barr()

        could arguably be improved by some-DSL-ish massaging.
        then again, who cares? it's just syntax.
    
    wtf #3:
        consider the utter madness of _invoke_macro_auto_temps,
        and all its trappings. reflect on how the same functionality
        could be obtained by passing stack_manager as another argument
        to all builtin macro definitions, next to machine, so that
        the macro body could just allocate and release its own temporaries.
        consider how that would remove the need for:
            i)      inspection of builting macro argument names
            ii)     ad-hoc semantics attatched to _tmp argument names
            iii)    dependency propagation of _tmp arguments to all builtin
            macros that call other builtin macros
"""

import inspect

def make_stack_address(offset):
    return ('stack_address', offset)

def is_stack_address(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'stack_address'
        offset = int(x[1])
    except Exception:
        return False
    return True

def match_stack_address(x):
    assert is_stack_address(x)
    return x[1]

def assert_no_aliasing(*args):
    assert len(args) == len(list(set(args)))

def make_constant(x):
    return ('constant', int(x))

def is_constant(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'constant'
        const = int(x[1])
    except Exception:
        return False
    return True

def match_constant(x):
    assert is_constant(x)
    return x[1]

def make_string_constant(x):
    return ('string_constant', str(x))

def is_string_constant(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'string_constant'
        const = str(x[1])
    except Exception:
        return False
    return True

def match_string_constant(x):
    assert is_string_constant(x)
    return x[1]

class Machine:
    def __init__(self, n_cells):
        self.n_cells = n_cells
        self.bf_ptr = 0
        self.stack_ptr = 0
        self.code = []
        self.loop_stack = []

    def validate(self):
        assert 0 <= self.bf_ptr < self.n_cells

    def do_move(self, offset):
        if offset == 0:
            pass
        elif offset > 0:
            self.code.append('>' * offset)
        else:
            self.code.append('<' * (-offset))
        self.bf_ptr += offset
        self.validate()

    def do_move_to_stack_address(self, stack_offset):
        dst_ptr = self.stack_ptr + stack_offset
        offset = dst_ptr - self.bf_ptr
        self.do_move(offset)

    def do_left(self):
        self.do_move(-1)

    def do_right(self):
        self.do_move(1)

    def do_inc(self, n = 1):
        assert n >= 0
        if n > 0:
            self.code.append('+' * n)
        self.validate()

    def do_dec(self, n = 1):
        assert n >= 0
        if n > 0:
            self.code.append('-' * n)
        self.validate()

    def do_begin_loop(self):
        self.code.append('[')
        self.loop_stack.append(self.bf_ptr)
        self.validate()

    def do_end_loop(self):
        self.code.append(']')
        # invariant : bf_ptr must have the same value
        # after [x] for all executation paths
        assert self.loop_stack.pop() == self.bf_ptr
        self.validate()

    def do_read(self):
        self.code.append(',')
        self.validate()

    def do_write(self):
        self.code.append('.')
        self.validate()

    def do_unvalidated_bf(self, bf_opcodes):
        known_opcodes = '<>+-[].,'
        for c in bf_opcodes:
            assert c in known_opcodes
        self.code.append(raw_bf_opcodes)

    def dump_code(self):
        print ''.join(self.code)

_BUILT_IN_MACROS = {}

def _invoke_macro(machine, macro_name, *args):
    if macro_name not in _BUILT_IN_MACROS:
        raise KeyError('unknown builtin macro : %s' % repr(macro_name))
    _BUILT_IN_MACROS[macro_name](machine, *args)

def _get_builtin_macro_args(macro_name):
    if macro_name not in _BUILT_IN_MACROS:
        raise KeyError('unknown builtin macro : %s' % repr(macro_name))
    args = inspect.getargspec(_BUILT_IN_MACROS[macro_name]).args
    formal_args = {}
    temp_args = {}
    for i, name in enumerate(args):
        if name == 'machine':
            pass
        elif name.startswith('_tmp'):
            temp_args[i] = name
        else:
            formal_args[i] = name
    return (formal_args, temp_args)

def _invoke_macro_auto_temps(machine, alloc_temp, free_temp, macro_name, *args):
    formal_args, temp_args = _get_builtin_macro_args(macro_name)
    assert len(args) == len(formal_args)
    n_macro_args = len(formal_args) + len(temp_args) + 1
    macro_args = [None] * n_macro_args
    for i in sorted(temp_args):
        macro_args[i] = alloc_temp()
    for j, i in enumerate(sorted(formal_args)):
        macro_args[i] = args[j]
    _invoke_macro(machine, macro_name, *macro_args[1:])
    for i in sorted(temp_args):
        free_temp(macro_args[i])

def BUILT_IN_MACRO(f):
    _BUILT_IN_MACROS[f.__name__] = f
    return f

@BUILT_IN_MACRO
def clear(machine, dst):
    a = match_stack_address(dst)
    machine.do_move_to_stack_address(a)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_end_loop()

@BUILT_IN_MACRO
def destructive_add(machine, src, dst):
    a = match_stack_address(src)
    b = match_stack_address(dst)
    assert_no_aliasing(a, b)
    machine.do_move_to_stack_address(a)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(b)
    machine.do_inc()
    machine.do_move_to_stack_address(a)
    machine.do_end_loop()

@BUILT_IN_MACRO
def destructive_sub(machine, src, dst):
    a = match_stack_address(src)
    b = match_stack_address(dst)
    assert_no_aliasing(a, b)
    machine.do_move_to_stack_address(a)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(b)
    machine.do_dec()
    machine.do_move_to_stack_address(a)
    machine.do_end_loop()

@BUILT_IN_MACRO
def move(machine, src, dst):
    _invoke_macro(machine, 'clear', dst)
    _invoke_macro(machine, 'destructive_add', src, dst)

@BUILT_IN_MACRO
def copy(machine, src, dst, _tmp0):
    a = match_stack_address(src)
    b = match_stack_address(dst)
    c = match_stack_address(_tmp0)
    assert_no_aliasing(a, b, c)
    _invoke_macro(machine, 'clear', dst)
    _invoke_macro(machine, 'clear', _tmp0)
    machine.do_move_to_stack_address(a)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(b)
    machine.do_inc()
    machine.do_move_to_stack_address(c)
    machine.do_inc()
    machine.do_move_to_stack_address(a)
    machine.do_end_loop()
    _invoke_macro(machine, 'destructive_add', _tmp0, src)

@BUILT_IN_MACRO
def stack_add(machine, src, dst, _tmp0, _tmp1):
    _invoke_macro(machine, 'copy', src, _tmp0, _tmp1)
    _invoke_macro(machine, 'destructive_add', _tmp0, dst)

@BUILT_IN_MACRO
def constant_add(machine, src, dst):
    a = match_constant(src)
    b = match_stack_address(dst)
    machine.do_move_to_stack_address(b)
    machine.do_inc(a)

@BUILT_IN_MACRO
def stack_sub(machine, src, dst, _tmp0, _tmp1):
    _invoke_macro(machine, 'copy', src, _tmp0, _tmp1)
    _invoke_macro(machine, 'destructive_sub', _tmp0, dst)

@BUILT_IN_MACRO
def constant_sub(machine, src, dst):
    a = match_constant(src)
    b = match_stack_address(dst)
    machine.do_move_to_stack_address(b)
    machine.do_dec(a)

@BUILT_IN_MACRO
def as_logical(machine, src, dst, _tmp0):
    a = match_stack_address(src)
    b = match_stack_address(dst)
    c = match_stack_address(_tmp0)
    assert_no_aliasing(a, b, c)
    _invoke_macro(machine, 'copy', src, _tmp0, dst)
    machine.do_move_to_stack_address(c)
    machine.do_begin_loop()
    machine.do_move_to_stack_address(b)
    machine.do_inc()
    _invoke_macro(machine, 'clear', _tmp0)
    machine.do_end_loop()

@BUILT_IN_MACRO
def logical_not(machine, src, dst, _tmp0):
    a = match_stack_address(src)
    b = match_stack_address(dst)
    c = match_stack_address(_tmp0)
    assert_no_aliasing(a, b, c)
    _invoke_macro(machine, 'copy', src, _tmp0, dst)
    machine.do_move_to_stack_address(b)
    machine.do_inc()
    machine.do_move_to_stack_address(c)
    machine.do_begin_loop()
    machine.do_move_to_stack_address(b)
    machine.do_dec()
    _invoke_macro(machine, 'clear', _tmp0)
    machine.do_end_loop()

@BUILT_IN_MACRO
def logical_or(machine, src_a, src_b, dst, _tmp0, _tmp1, _tmp2):
    # much stuffing about to ensure we leave src_a, src_b untouched
    # but we operate on their 'as_logical' values
    _invoke_macro(machine, 'clear', dst)
    _invoke_macro(machine, 'as_logical', src_a, _tmp0, _tmp1)
    _invoke_macro(machine, 'stack_add', src_a, dst, _tmp1, _tmp2)
    _invoke_macro(machine, 'as_logical', src_b, _tmp0, _tmp1)
    _invoke_macro(machine, 'stack_add', src_b, dst, _tmp1, _tmp2)
    _invoke_macro(machine, 'as_logical', dst, _tmp0, _tmp1)
    _invoke_macro(machine, 'move', _tmp0, dst)

@BUILT_IN_MACRO
def logical_and(machine, src_a, src_b, dst, _tmp0, _tmp1, _tmp2):
    _invoke_macro(machine, 'clear', dst)
    _invoke_macro(machine, 'logical_not', src_a, _tmp0, _tmp1)
    _invoke_macro(machine, 'stack_add', src_a, dst, _tmp1, _tmp2)
    _invoke_macro(machine, 'logical_not', src_b, _tmp0, _tmp1)
    _invoke_macro(machine, 'stack_add', src_b, dst, _tmp1, _tmp2)
    _invoke_macro(machine, 'logical_not', dst, _tmp0, _tmp1)
    _invoke_macro(machine, 'move', _tmp0, dst)

class StackManager:
    def __init__(self):
        self._occupied_offsets = set()

    def _first_free_offset(self):
        i = 0
        while i in self._occupied_offsets:
            i += 1
        return i
    
    def allocate_local(self):
        offset = self._first_free_offset()
        self._occupied_offsets.add(offset)
        return make_stack_address(offset)

    def free_local(self, stack_address):
        offset = match_stack_address(stack_address)
        assert offset in self._occupied_offsets
        self._occupied_offsets.remove(offset)

def test():
    print 'Test macro argument extraction:'
    res = _get_builtin_macro_args('logical_and')
    print str(res)

    print 'Test {clear stack 5, clear stack 3}'
    dst_a = ('stack_address', 5)
    dst_b = ('stack_address', 3)
    machine = Machine(n_cells = 10)
    _invoke_macro(machine, 'clear', dst_a)
    _invoke_macro(machine, 'clear', dst_b)
    machine.dump_code()

    print 'Test {c = logical_or(a, b)} with manual temp management'
    var_a = ('stack_address', 0)
    var_b = ('stack_address', 1)
    var_c = ('stack_address', 2)
    var_tmp0 = ('stack_address', 3)
    var_tmp1 = ('stack_address', 4)
    var_tmp2 = ('stack_address', 5)
    machine = Machine(n_cells = 10)
    _invoke_macro(machine, 'logical_or', var_a, var_b, var_c, var_tmp0, var_tmp1, var_tmp2)
    machine.dump_code()

    print 'Test {c = logical_and(a, b)} with automatic temp management'
    stack_man = StackManager()
    var_a = stack_man.allocate_local()
    var_b = stack_man.allocate_local()
    var_c = stack_man.allocate_local()
    machine = Machine(n_cells = 10)
    _invoke_macro_auto_temps(machine, stack_man.allocate_local,
        stack_man.free_local, 'logical_and', var_a, var_b, var_c)
    machine.dump_code()



if __name__ == '__main__':
    test()
