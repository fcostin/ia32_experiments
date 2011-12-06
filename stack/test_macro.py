# prototypical macro-language example, as dsl of python.

from prelude import *

def_macro('inc_by_one', 'x')(
    local('unused'),
    constant_add(constant(1), 'x'),
)

def_macro('inc_by_seven', 'a')(
    macro('inc_by_one', 'a'),
    macro('inc_by_one', 'a'),
    macro('inc_by_one', 'a'),
    macro('inc_by_one', 'a'),
    macro('inc_by_one', 'a'),
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
    begin_loop('n'),
    constant_sub(constant(1), 'n'),
    put_string_constant(string_constant('boogaloo!\n')),
    end_loop('n'),
)

debug_dump()
