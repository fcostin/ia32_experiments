def is_user_macro(user_macro):
    return (len(user_macro) == 4) and (user_macro[0] == 'user_macro')

def is_macro_call(expr):
    return (len(expr) == 3) and (expr[0] == 'macro_call')

def is_local_declaration(expr):
    return is_macro_call(expr) and expr[1] == 'local' and len(expr[2]) == 1

def match_local_declaration(expr):
    assert is_local_declaration(expr)
    return expr[2][0]

def get_user_macro_locals(user_macro):
    assert is_user_macro(user_macro)
    macro_locals = []
    _, _, _, body = user_macro
    for expr in body:
        if is_local_declaration(expr):
            local_name = match_local_declaration(expr)
            assert local_name not in macro_locals
            macro_locals.append(local_name)
    return macro_locals

def get_user_macro_arguments(user_macro):
    assert is_user_macro(user_macro)
    return list(user_macro[2])

def instantiate_locals(user_macro, unique_var_names):
    macro_locals = get_user_macro_locals(user_macro)
    _, user_macro_name, user_macro_args, body = user_macro
    body_prime = []
    for expr in body:
        if is_local_declaration(expr):
            local_name = match_local_declaration(expr)
            body_prime.append(('allocate_var', unique_var_names[local_name]))
        elif is_macro_call(expr):
            _, macro_name, expr_args = expr
            expr_args_prime = []
            for arg in expr_args:
                if arg in macro_locals:
                    arg_prime = ('var', unique_var_names[arg])
                else:
                    arg_prime = arg
                expr_args_prime.append(arg_prime)
            body_prime.append(('macro_call', macro_name, expr_args_prime))
        else:
            body_prime.append(expr)
    for local_name in macro_locals:
        body_prime.append(('destroy_var', unique_var_names[local_name]))
    user_macro_prime = ('user_macro', user_macro_name, user_macro_args, body_prime)
    return user_macro_prime

def test_compile(user_macro):
    """
    XXX TODO : expand macro_call expressions
        two cases:
            case 1: macro being called is user macro.
                in this case, need to inline the user macro
                substituting the arguments through the inlined body
            case 2: macro being called is builtin macro.
                in this case defer the work for the moment
                replace the 'macro_call' expression with a
                'builtin_macro_call' expression, say.
    XXX TODO : need to code up serious name substitution thing that
        actually does correctly substitute unique names throughout
        the entire compiled program, not just per macro
    """
    macro_locals = get_user_macro_locals(user_macro)
    unique_var_names = dict((x, '%s_dummy_123' % x) for x in macro_locals)
    return instantiate_locals(user_macro, unique_var_names)
