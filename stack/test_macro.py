# prototypical macro-language example, as dsl of python.

from prelude import *

def_macro('inc_by_one', 'x')(
    local('dummy'),
    local('another_dummy'),
    copy('x', 'another_dummy'),
    copy('x', 'dummy'),
    constant_add(constant(1), 'x'),
)

def_macro('inc_by_seven', 'a')(
    macro('inc_by_one', 'a'),
    constant_add(constant(4), 'a'),
    macro('inc_by_one', 'a'),
    macro('inc_by_one', 'a'),
)

def_macro('main')(
	local('x'),
	get_char('x'),
	macro('inc_by_seven', 'x'),
	put_char('x'),
    put_string_constant(string_constant('hello world!\n')),
    put_string_constant(string_constant('input a digit:\n')),
    local('n'),
    get_char('n'),
    constant_sub(char_constant('0'), 'n'),
    while_nonzero('n')(
        constant_sub(constant(1), 'n'),
        put_string_constant(string_constant('boogaloo!\n')),
        grow_stack(constant(1)),
        local('z'),
        copy(stack_address(-1), 'z'),
        constant_add(char_constant('0'), 'z'),
        put_char('z'),
    ),
    put_string_constant(string_constant('enter "a" if you like:\n')),
    local('maybe_a'),
    get_char('maybe_a'),
    constant_sub(char_constant('a'), 'maybe_a'),
    local('t'),
    logical_not('maybe_a', 't'),
    if_nonzero('t')(
        put_string_constant(string_constant('\nyup, that was an "a"\n')),
    ),
    if_nonzero('maybe_a')(
        put_string_constant(string_constant('\nno "a" today eh?\n')),
    ),
)

# start compilation process ...
debug_dump()
