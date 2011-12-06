import itertools
import codegen

def is_user_macro(user_macro):
    return (len(user_macro) == 4) and (user_macro[0] == 'user_macro')

def is_macro_call(expr):
    return (len(expr) == 3) and (expr[0] == 'macro_call')

def match_macro_call(expr):
    assert is_macro_call(expr)
    return expr[1:]

def is_local_declaration(expr):
    return is_macro_call(expr) and expr[1] == 'local' and len(expr[2]) == 1

def match_local_declaration(expr):
    assert is_local_declaration(expr)
    return expr[2][0]

def is_allocate_var(expr):
    return (len(expr) == 2) and (expr[0] == 'allocate_var')

def match_allocate_var(expr):
    assert is_allocate_var(expr)
    return expr[1]

def is_destroy_var(expr):
    return (len(expr) == 2) and (expr[0] == 'destroy_var')

def match_destroy_var(expr):
    assert is_destroy_var(expr)
    return expr[1]

def is_var(expr):
    return (len(expr) == 2) and (expr[0] == 'var')

def match_var(expr):
    assert is_var(expr)
    return expr[1]


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

def augment_local_declarations_with_alloc_delete(user_macro):
    macro_locals = get_user_macro_locals(user_macro)
    _, user_macro_name, user_macro_args, body = user_macro
    body_prime = []
    for expr in body:
        if is_local_declaration(expr):
            local_name = match_local_declaration(expr)
            assert local_name in macro_locals
            # augment local declaration with allocate
            # n.b. we dont remove the local declaration here
            # as that way we can still use it to signal
            # the name of the local. it will be removed
            # later when locals are instantiated with
            # unique names
            body_prime.append(expr)
            body_prime.append(('allocate_var', local_name))
        else:
            body_prime.append(expr)
    for local_name in macro_locals:
        body_prime.append(('destroy_var', local_name))
    user_macro_prime = ('user_macro', user_macro_name, user_macro_args, body_prime)
    return user_macro_prime

def instantiate_locals(user_macro, unique_var_names):
    macro_locals = get_user_macro_locals(user_macro)
    _, user_macro_name, user_macro_args, body = user_macro
    body_prime = []
    for expr in body:
        if is_local_declaration(expr):
            pass
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
        elif is_allocate_var(expr):
            var_name = match_allocate_var(expr)
            if var_name in macro_locals:
                var_name = unique_var_names[var_name]
            expr_prime = ('allocate_var', var_name)
            body_prime.append(expr_prime)
        elif is_destroy_var(expr):
            var_name = match_destroy_var(expr)
            if var_name in macro_locals:
                var_name = unique_var_names[var_name]
            expr_prime = ('destroy_var', var_name)
            body_prime.append(expr_prime)
        else:
            body_prime.append(expr)
    user_macro_prime = ('user_macro', user_macro_name, user_macro_args, body_prime)
    return user_macro_prime

def count_user_macro_calls(declared_user_macros, user_macro):
    assert is_user_macro(user_macro)
    _, user_macro_name, user_macro_args, body = user_macro
    
    count = 0
    for expr in body:
        if is_macro_call(expr):
            call_name, call_args = match_macro_call(expr)
            assert call_name is not user_macro_name # no recursion since we inline everything!
            if call_name in declared_user_macros:
                count += 1
    return count

def instantiate_arguments(user_macro, arg_replacements):
    _, user_macro_name, user_macro_args, body = user_macro
    body_prime = []
    for expr in body:
        if is_macro_call(expr):
            _, macro_name, expr_args = expr
            expr_args_prime = []
            for arg in expr_args:
                if arg in user_macro_args:
                    arg_prime = arg_replacements[arg]
                else:
                    arg_prime = arg
                expr_args_prime.append(arg_prime)
            body_prime.append(('macro_call', macro_name, expr_args_prime))
        else:
            body_prime.append(expr)
    user_macro_prime = ('user_macro', user_macro_name, user_macro_args, body_prime)
    return user_macro_prime

def expand_one_user_macro_call(declared_user_macros, user_macro):
    assert count_user_macro_calls(declared_user_macros, user_macro)
    _, user_macro_name, user_macro_args, body = user_macro
    body_prime = []
    has_expanded = False
    for expr in body:
        if is_macro_call(expr):
            _, macro_name, expr_args = expr
            if (macro_name in declared_user_macros) and not has_expanded:
                print 'expanding user macro ...'
                callee = declared_user_macros[macro_name]
                callee = augment_local_declarations_with_alloc_delete(callee)
                _, _, callee_args, _ = callee
                assert len(expr_args) == len(callee_args)
                arg_replacements = dict(zip(callee_args, expr_args))
                instantiated_macro = instantiate_arguments(callee, arg_replacements)
                _, _, _, inlined_macro_body = instantiated_macro
                body_prime += list(inlined_macro_body)
                has_expanded = True
            else:
                body_prime.append(expr)
        else:
            body_prime.append(expr)
    assert has_expanded
    user_macro_prime = ('user_macro', user_macro_name, user_macro_args, body_prime)
    return user_macro_prime

def translate_to_brainfuck_opcodes(main_program):
    n_cells = 30000
    stack_man = codegen.StackManager()
    machine = codegen.Machine(n_cells)

    assert is_user_macro(main_program)
    _, _, _, body = main_program

    allocated_vars = {}

    for expr in body:
        if is_allocate_var(expr):
            var_name = match_allocate_var(expr)
            assert var_name not in allocated_vars
            allocated_vars[var_name] = stack_man.allocate_local()
        elif is_destroy_var(expr):
            var_name = match_destroy_var(expr)
            assert var_name in allocated_vars
            stack_man.free_local(allocated_vars[var_name])
            del allocated_vars[var_name]
        elif is_macro_call(expr):
            macro_name, macro_args = match_macro_call(expr)
            allocated_args = []
            for arg in macro_args:
                if is_var(arg):
                    var_name = match_var(arg)
                    allocated_args.append(allocated_vars[var_name])
                else:
                    allocated_args.append(arg)
            codegen._invoke_macro_auto_temps(machine, stack_man, macro_name, *allocated_args)
        else:
            raise ValueError('unexpected expr type')
    return machine.code

def formatted_code(code):
    code = ''.join(code)
    line_width = 30
    lines = []
    while len(code) > line_width:
        lines.append(code[:line_width])
        code = code[line_width:]
    if code:
        lines.append(code)
    return ''.join(map(lambda s : s + '\n', lines))

def test_compile_program(builtin_macros, user_macros, entry_point):
    unique_names = itertools.count()

    def uniquify_name(x):
        return '%s_%d' % (str(x), unique_names.next())

    def fully_expand(user_macro):
        macro_locals = get_user_macro_locals(user_macro)
        user_macro = augment_local_declarations_with_alloc_delete(user_macro)
        uniquified_names = dict((x, uniquify_name(x)) for x in macro_locals)
        user_macro = instantiate_locals(user_macro, uniquified_names)
        while count_user_macro_calls(user_macros, user_macro):
            user_macro = expand_one_user_macro_call(user_macros, user_macro)
            macro_locals = get_user_macro_locals(user_macro)
            uniquified_names = dict((x, uniquify_name(x)) for x in macro_locals)
            user_macro = instantiate_locals(user_macro, uniquified_names)
        return user_macro
   
    # Compilation pass 1:
    #   replace local declarations with allocate / destroy pairs
    #   uniquify local variable names
    #   expand all user macro calls inline
    print 'compiler pass 1: reducing main macro'
    main_program = fully_expand(user_macros[entry_point])
    
    # Compilation pass 2:
    #   translate into brainfuck opcodes
    print 'compiler pass 2: generating code'
    code = translate_to_brainfuck_opcodes(main_program)
    return (main_program, formatted_code(code))
