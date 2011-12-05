# prototypical macro-language example, as dsl of python.

from prelude import *

def_macro('inc_by_seven', 'a')(
	constant_add(literal(7), 'a'),
)

def_macro('main')(
	local('x'),
	get_char('x'),
	macro('inc_by_seven', 'x'),
	put_char('x'),
)

debug_dump()
