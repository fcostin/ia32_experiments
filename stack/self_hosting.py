from prelude import *

def_macro('update_input', 'c')(
    clear('c'),
    get_char('c'),
)

def_macro('is_equal', 'const', 'src', 'dst')(
    local('temp'),
    copy('src', 'temp'),
    constant_sub('const', 'temp'),
    logical_not('temp', 'dst'),
)

def_macro('main')(
    local('c'),
    macro('update_input', 'c'),
    # put_string_constant(string_constant('BEGIN\n')),
    while_nonzero('c')(
        local('match'),
        macro('is_equal', char_constant('+'), 'c', 'match'), 
        if_nonzero('match')(
            put_string_constant(string_constant('INC\n')),
        ),
        macro('is_equal', char_constant('-'), 'c', 'match'), 
        if_nonzero('match')(
            put_string_constant(string_constant('DEC\n')),
        ),
        macro('update_input', 'c'),
    ),
    # put_string_constant(string_constant('END\n')),
)

debug_dump()
