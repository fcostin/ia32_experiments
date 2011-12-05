"""
TODO

1.  need a way to define macros
        macro is probably the best name
        because they're always going to be inline functions
        so macro brings the right semantic baggage for people with C experience

    no way to dynamically define things - these are all compile time definitions

2.  need a way to translate a program of low level operations
        (in terms of the basic operations acing on fixed concrete memory locations
        with respect to the stack pointer)
    into brainfuck opcodes
    This means figuring out the explicit movement of brainfuck's pointer

3.  need to define some sane way of handling variable name collisions
    solution[?]:
        use nested environments
        perform name lookup inner -> outer
        stop at first successful lookup
        what is value of lookup? memory location.
"""

# what do we need to do to translate
# ['clear', 'a'] into concrete bf code?
# we need to know
#   i)      the location of bf's pointer
#   ii)     the position of our stack pointer
#   iii)    the storage location of a with respect to that stack pointer

def f(*args, **kwargs):
    return (args, kwargs)

def declare_expression(name, env):
    assert name not in env
    def make_expression(name):
        def expression(*args, **kwargs):
            return (name, args, kwargs)
        return expression
    env[name] = make_expression(name)

expression_names = [
    'new_local',
    'delete_local',
    'get_char',
    'print_char',
    'while_nonzero',
]

for name in expression_names:
    # !!! XXX !!! XXX patches globals XXX !!!
    declare_expression(name, env = globals())

# echo loop test
echo_loop = [
    new_local('t0'),
    get_char(dest = 't0'),
    while_nonzero('t0', [
            print_char('t0'),
            get_char(dest = 't0'),
        ]
    ),
    delete_local('t0'),
]

class LocalStorage:
    def __init__(self):
        self.index_to_local = {}
        self.local_to_index = {}

    def next_free_index(self):
        i = 0
        while i in self.index_to_local:
            i += 1
        return i

    def allocate(self, name):
        assert name not in self.local_to_index
        i = self.next_free_index()
        self.index_to_local[i] = name
        self.local_to_index[name] = i
        return i

    def deallocate(self, name):
        assert name in self.local_to_index
        i = self.local_to_index[name]
        del self.local_to_index[name]
        del self.index_to_local[i]

    def get_location(self, name):
        assert name in self.local_to_index
        return ('local', name, self.local_to_index[name])

def compile(stack_pointer, local_storage, block):

    locate = lambda var_name : local_storage.get_location(var_name)

    def compile_new_local(args, kwargs):
        assert len(args) == 1
        assert len(kwargs) == 0
        name = args[0]
        local_storage.allocate(name)
        return ()

    def compile_delete_local(args, kwargs):
        assert len(args) == 1
        assert len(kwargs) == 0
        name = args[0]
        local_storage.deallocate(name)
        return ()

    def compile_while_block(args, kwargs):
        assert len(args) == 2
        assert len(kwargs) == 0
        var_name, while_block = args
        var_location = locate(var_name)
        yield ('%%begin_while_block', var_location)
        for x in compile(stack_pointer, local_storage, while_block):
            yield x
        yield ('%%end_while_block', var_location)

    def compile_macro(name, args, kwargs):
        located_args = map(locate, args)
        located_kwargs = dict((k, locate(v)) for (k, v) in kwargs.iteritems())
        yield ('%%macro', name, located_args, located_kwargs)

    dispatch = {
        'new_local' : compile_new_local,
        'delete_local' : compile_delete_local,
        'while_nonzero' : compile_while_block,
    }
    for expr in block:
        if expr[0] in dispatch:
            for x in dispatch[expr[0]](expr[1], expr[2]):
                yield x
        else:
            for x in compile_macro(expr[0], expr[1], expr[2]):
                yield x

local_storage = LocalStorage()

for x in compile(0, local_storage, echo_loop):
    print str(x)

