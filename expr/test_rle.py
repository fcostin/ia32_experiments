from prelude import *

# ------------ input stuff ------------------

DEF_MACRO('input_init', 'n', 'c', 'c_next')(
    CLEAR('c'),
    CLEAR('n'),
    GET_CHAR('c_next'),
    CALL('input_update', 'n', 'c', 'c_next'),
)

DEF_MACRO('input_update', 'n', 'c', 'c_next')(
    # while n is zero or c_next == c, accumulate n
    LOCAL('n_is_zero'),
    LOGICAL_NOT('n', 'n_is_zero'),
    LOCAL('not_match'),
    STACK_SUB('c', 'c_next', 'not_match'),
    LOCAL('match'),
    LOGICAL_NOT('not_match', 'match'),
    LOCAL('merge_ok'),
    LOGICAL_OR('n_is_zero', 'match', 'merge_ok'),
    WHILE('merge_ok')(
        COPY('c_next', 'c'),
        CONSTANT_ADD(INT_CONSTANT(1), 'n'),
        CLEAR('merge_ok'),
        # but stop if c_next is zero (EOF)
        IF('c_next')(
            CLEAR('c_next'),
            GET_CH('c_next'),
            STACK_SUB('c', 'c_next', 'not_match'),
            LOGICAL_NOT('not_match', 'match'),
        ),
    ),
)

DEF_MACRO('input_next_char', 'n', 'c', 'c_next', 'result_c')(
    # need something here like "assert n > 0"
    LOCAL('not_n'),
    LOGICAL_NOT('n', 'not_n'),
    IF('not_n')(
        CALL('input_update', 'n', 'c', 'c_next'),
    ),
    COPY('c', 'result_c'),
    CONSTANT_SUB(INT_CONSTANT(1), 'n'),
    # call update on input ...
)

DEF_MACRO('input_next_run', 'n', 'c', 'c_next', 'result_n', 'result_c')(
    COPY('n', 'result_n'),
    COPY('c', 'result_c'),
    CALL('input_update', 'n', 'c', 'c_next'),
)

DEF_MACRO('main')(
    LOCAL('input0'),
    LOCAL('input1'),
    LOCAL('input2'),
    CALL('input_init', 'input0', 'input1', 'input2'),
    LOCAL('c'),
    CALL('input_next_char', 'input0', 'input1', 'input2', 'c'),
    WHILE('c')(
        PUT_STRING_CONSTANT(STRING_CONSTANT('got "')),
        PUT_CHAR('c'),
        PUT_STRING_CONSTANT(STRING_CONSTANT('"\n')),
        CALL('input_next_char', 'input0', 'input1', 'input2', 'c'),
    ),
)

test_compile()
