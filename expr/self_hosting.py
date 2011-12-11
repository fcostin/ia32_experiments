from prelude import *

DEF_MACRO('counter_init', 'x0', 'x1')(
   CLEAR('x0'),
   CLEAR('x1'),
)

DEF_MACRO('counter_inc', 'x0', 'x1')(
    CONSTANT_ADD(INT_CONSTANT(1), 'x0'),
    LOCAL('test'),
    LOGICAL_NOT('x0', 'test'),
    IF('test')(
        CLEAR('x0'),
        CONSTANT_ADD(INT_CONSTANT(1), 'x1'),
    )
)

DEF_MACRO('update_input', 'c')(
    CLEAR('c'),
    GET_CHAR('c'),
)

DEF_MACRO('is_equal', 'const', 'src', 'dst')(
    LOCAL('temp'),
    COPY('src', 'temp'),
    CONSTANT_SUB('const', 'temp'),
    LOGICAL_NOT('temp', 'dst'),
)

DEF_MACRO('main')(
    LOCAL('c'),
    CALL('update_input', 'c'),
    PUT_STRING_CONSTANT(STRING_CONSTANT('BEGIN\n')),
    WHILE('c')(
        LOCAL('match'),
        CALL('is_equal', CHAR_CONSTANT('+'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('INC\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT('-'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('DEC\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT('<'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('LEFT\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT('>'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('RIGHT\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT('['), 'c', 'match'), 
        IF('match')(
            GROW_STACK(INT_CONSTANT(1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT('BEGIN_LOOP\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT(']'), 'c', 'match'), 
        IF('match')(
            SHRINK_STACK(INT_CONSTANT(1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT('END_LOOP\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT(','), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('READ\n')),
        ),
        CALL('is_equal', CHAR_CONSTANT('.'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT('WRITE\n')),
        ),
        CALL('update_input', 'c'),
    ),
    PUT_STRING_CONSTANT(STRING_CONSTANT('END\n')),
)

test_compile()
