from prelude import *

# compute quotient of x div y
DEF_MACRO('div_q', 'x', 'y', 'q')(
    LOCAL('r'),
    CLEAR('q'),
    COPY('x', 'r'),
    LOCAL('t'),
    AS_LOGICAL('r', 't'),
    WHILE('t')(
        LOCAL('i'),
        COPY('y', 'i'),
        LOCAL('t2'),
        LOGICAL_AND('i', 't', 't2'),
        WHILE('t2')(
            CONSTANT_SUB(INT_CONSTANT(1), 'i'),
            CONSTANT_SUB(INT_CONSTANT(1), 'r'),
            AS_LOGICAL('r', 't'),
            LOGICAL_AND('i', 't', 't2'),
        ),
        LOCAL('t3'),
        LOGICAL_NOT('i', 't3'),
        IF('t3')(
            CONSTANT_ADD(INT_CONSTANT(1), 'q'),
        ),
        # else break outer loop
        LOCAL('t4'),
        LOGICAL_NOT('t3', 't4'),
        IF('t4')(
            CLEAR('t'),
        )
    )
)

# compute remainder of x div y, given quotient q
DEF_MACRO('div_r', 'x', 'y', 'q', 'r')(
    COPY('x', 'r'),
    LOCAL('i'),
    COPY('q', 'i'),
    WHILE('i')(
        STACK_SUB('y', 'r'),
        CONSTANT_SUB(INT_CONSTANT(1), 'i'),
    ),
)

# compute quotient and remainder of x div y
DEF_MACRO('div', 'x', 'y', 'q', 'r')(
    CALL('div_q', 'x', 'y', 'q'),
    CALL('div_r', 'x', 'y', 'q', 'r'),
)

DEF_MACRO('update_input', 'c')(
    CLEAR('c'),
    GET_CHAR('c'),
)

DEF_MACRO('main')(
    LOCAL('x'),
    CALL('update_input', 'x'),
    CONSTANT_SUB(CHAR_CONSTANT('0'), 'x'),
    LOCAL('y'),
    CALL('update_input', 'y'),
    CONSTANT_SUB(CHAR_CONSTANT('0'), 'y'),
    LOCAL('q'),
    LOCAL('r'),
    CALL('div', 'x', 'y', 'q', 'r'),
    PUT_STRING_CONSTANT(STRING_CONSTANT('\nquotient = ')),
    CONSTANT_ADD(CHAR_CONSTANT('0'), 'q'),
    PUT_CHAR('q'),
    PUT_STRING_CONSTANT(STRING_CONSTANT('\nremainder = ')),
    CONSTANT_ADD(CHAR_CONSTANT('0'), 'r'),
    PUT_CHAR('r'),
    PUT_STRING_CONSTANT(STRING_CONSTANT('\n')),
)

test_compile()
