"""
the idea is to import * from here & then start writing code in a silly macro-language
"""
import macro_compiler

_BUILT_IN_MACROS = {
    'constant_add' : None,
    'local' : None,
    'get_char' : None,
    'put_char' : None,
}

def __make_macro_call_capturer(macro_name):
    def __macro_call_capturer(*args):
        return ('macro_call', macro_name, args)
    return __macro_call_capturer

def __register_all_builtin_macros():
    for name in _BUILT_IN_MACROS:
        globals()[name] = __make_macro_call_capturer(name)

__register_all_builtin_macros()

_USER_MACROS = {}

def __make_user_macro(macro_name, args, body):
    return ('user_macro', macro_name, args, body)

def __add_user_macro(macro_name, args, body):
    user_macro = __make_user_macro(macro_name, args, body)
    _USER_MACROS[macro_name] = user_macro

def def_macro(macro_name, *args):
    def capture_body(*body):
        __add_user_macro(macro_name, args, body)
    return capture_body

def macro(macro_name, *args):
    return ('macro_call', macro_name, args)

def literal(x):
    return ('literal', int(x))

def char_literal(x):
    return ('literal', ord(x))

def string_literal(x):
    return ('string_literal', str(x))

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

    print '_COMPILED_MACROS:'
    compiled_macros = {}
    for key in sorted(_USER_MACROS):
        compiled_macros[key] = macro_compiler.test_compile(_USER_MACROS[key])
        debug_dump_user_macro(compiled_macros[key])
