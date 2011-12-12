from prelude import *
import ia32

# MATH DEFINITIONS

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

# COUNTER DEFINITIONS

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

# print hex digit x, 0 <= x < 16
DEF_MACRO('print_hex_digit', 'x')(
    LOCAL('y'),
    CLEAR('y'),
    CONSTANT_ADD(INT_CONSTANT(10),'y'),
    LOCAL('q'),
    LOCAL('r'),
    CALL('div', 'x', 'y','q','r'),
    IF('q')(
        CONSTANT_ADD(CHAR_CONSTANT('a'), 'r'),
    ),
    LOCAL('not_q'),
    LOGICAL_NOT('q', 'not_q'),
    IF('not_q')(
        CONSTANT_ADD(CHAR_CONSTANT('0'), 'r'),
    ),
    PUT_CHAR('r'),
)

DEF_MACRO('print_hex_byte', 'x')(
    LOCAL('y'),
    CLEAR('y'),
    CONSTANT_ADD(INT_CONSTANT(16),'y'),
    LOCAL('q'),
    LOCAL('r'),
    CALL('div', 'x', 'y','q','r'),
    CALL('print_hex_digit', 'q'),
    CALL('print_hex_digit', 'r'),
)

DEF_MACRO('counter_print', 'x0', 'x1')(
    CALL('print_hex_byte', 'x1'),
    CALL('print_hex_byte', 'x0'),
)

# INPUT DEFINITIONS

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
    LOCAL('name_counter_0'),
    LOCAL('name_counter_1'),
    CALL('counter_init', 'name_counter_0', 'name_counter_1'),
    LOCAL('c'),
    CALL('update_input', 'c'),
    PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.PROGRAM_START)),
    WHILE('c')(
        LOCAL('match'),
        CALL('is_equal', CHAR_CONSTANT('+'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.DP_INC)),
        ),
        CALL('is_equal', CHAR_CONSTANT('-'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.DP_DEC)),
        ),
        CALL('is_equal', CHAR_CONSTANT('<'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.DP_LEFT)),
        ),
        CALL('is_equal', CHAR_CONSTANT('>'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.DP_RIGHT)),
        ),
        CALL('is_equal', CHAR_CONSTANT('['), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.BEGIN_WHILE_1)),
            CALL('counter_print', 'name_counter_0', 'name_counter_1'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.BEGIN_WHILE_2)),
            CALL('counter_print', 'name_counter_0', 'name_counter_1'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.BEGIN_WHILE_3)),
            GROW_STACK(INT_CONSTANT(2)),
            COPY('name_counter_0', STACK_ADDRESS(-2)),
            COPY('name_counter_1', STACK_ADDRESS(-1)),
            CALL('counter_inc', 'name_counter_0', 'name_counter_1'),
        ),
        CALL('is_equal', CHAR_CONSTANT(']'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.END_WHILE_1)),
            CALL('counter_print', STACK_ADDRESS(-2), STACK_ADDRESS(-1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.END_WHILE_2)),
            CALL('counter_print', STACK_ADDRESS(-2), STACK_ADDRESS(-1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.END_WHILE_3)),
            SHRINK_STACK(INT_CONSTANT(2)),
        ),
        CALL('is_equal', CHAR_CONSTANT(','), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.READ_CHAR)),
        ),
        CALL('is_equal', CHAR_CONSTANT('.'), 'c', 'match'), 
        IF('match')(
            PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.WRITE_CHAR)),
        ),
        CALL('update_input', 'c'),
    ),
    PUT_STRING_CONSTANT(STRING_CONSTANT(ia32.PROGRAM_END)),
)

test_compile()
