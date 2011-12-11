from sugar import *

_USER_MACROS = {}

def DEF_MACRO(name, *params):
    def _capture_macro_body(*body):
        macro = MACRO(name, *params)(*body)
        _USER_MACROS[name] = macro
    return _capture_macro_body

def test_compile():
    import expr
    for macro_name in sorted(_USER_MACROS):
        macro = _USER_MACROS[macro_name]
        print '>> %s' % macro_name
        print
        expr.expr_print(macro)
        print
    main_macro = expr.compile_macro(_USER_MACROS, 'main')
    import compile
    import codegen
    compile.compile_phase_2(codegen._BUILT_IN_MACROS, main_macro)
