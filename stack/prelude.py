"""
the idea is to import * from here & then start writing code in a silly macro-language
"""
import macro_compiler
import codegen

_BUILT_IN_MACROS = dict(codegen._BUILT_IN_MACROS)
_BUILT_IN_MACROS['local'] = None
_BUILT_IN_MACRO_CALL_CAPTURERS = {}

def __make_macro_call_capturer(macro_name):
    def __macro_call_capturer(*args):
        # returning list of tuples instead of just one
        # tuple gives us flexibility in other places
        # to have things expand to more (or less?)
        # tuples ...
        return [('macro_call', macro_name, args)]
    return __macro_call_capturer

def __register_all_builtin_macros():
    for name in _BUILT_IN_MACROS:
        capturer = __make_macro_call_capturer(name)
        globals()[name] = capturer
        _BUILT_IN_MACRO_CALL_CAPTURERS[name] = capturer

__register_all_builtin_macros()

_USER_MACROS = {}

def __make_user_macro(macro_name, args, body):
    return ('user_macro', macro_name, args, body)

def __add_user_macro(macro_name, args, body):
    user_macro = __make_user_macro(macro_name, args, body)
    _USER_MACROS[macro_name] = user_macro

def def_macro(macro_name, *args):
    def capture_macro_body(*body):
        # merge lists of tuples into single list of tuples
        flattened_body = sum(map(list, body), [])
        __add_user_macro(macro_name, args, flattened_body)
    return capture_macro_body

def macro(macro_name, *args):
    return [('macro_call', macro_name, args)]

def constant(x):
    return ('constant', int(x))

def char_constant(x):
    return ('constant', ord(x))

def string_constant(x):
    return ('string_constant', str(x))

def stack_address(x):
    if x >= 0:
        raise ValueError('stack address must be negative (otherwise it will clobber locals)')
    return ('stack_address', int(x))

def while_nonzero(x):
    # syntactic sugar for begin loop / end loop
    def capture_while_body(*body):
        flattened_body = sum(map(list, body), [])
        return (_BUILT_IN_MACRO_CALL_CAPTURERS['begin_loop'](x) +
            flattened_body +
            _BUILT_IN_MACRO_CALL_CAPTURERS['end_loop'](x))
    return capture_while_body


def debug_dump_user_macro(user_macro):
    _, key, args, body = user_macro
    print '\t%s:' % key
    print '\t\targs: %s' % str(args)
    print '\t\tbody:'
    for x in body:
        print '\t\t\t%s' % str(x)
    macro_locals = macro_compiler.get_user_macro_locals(user_macro)
    print '\t\tlocals: %s' % str(macro_locals)

def debug_dump():
    print '_BUILT_IN_MACROS:'
    for key in sorted(_BUILT_IN_MACROS):
        print '\t%s' % key
    print '_USER_MACROS:'
    for key in sorted(_USER_MACROS):
        debug_dump_user_macro(_USER_MACROS[key])
    print 'COMPILING MAIN MACRO...'
    reduced_form, bf_code = macro_compiler.test_compile_program(_BUILT_IN_MACROS, _USER_MACROS, 'main')
    print 'OK'
    print 'REDUCED FORM OF MAIN MACRO:'
    debug_dump_user_macro(reduced_form)
    print 'BRAINFUCK CODE:'
    print bf_code
