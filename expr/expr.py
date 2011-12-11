from sugar import *
import pattern_match as pm

def expr_print(expr, indent = 0):
    prefix = '. ' * indent
    m = pm.match(L(pm.Star('x'))).attempt_match(expr)
    if m is not None:
        print '%sL %s' % (prefix, str(m['x']))
    else:
        m = pm.match(pm.Cons(pm.Star('head'), pm.Star('tail'))).attempt_match(expr)
        assert m is not None
        print '%sE %s' % (prefix, str(m['head']))
        for x in m['tail']:
            expr_print(x, indent + 1)


def expr_map_literals(f, expr, prefix = None):
    """
    replace expr with expr_prime, where
    each literal L(x) in expr is replaced with
    f(x, prefix), where prefix is the list of
    expression tags along the path from the
    expression root to the literal L(x)
    """
    if prefix is None:
        prefix = []
    m = pm.match(L(pm.Star('x'))).attempt_match(expr)
    if m is not None:
        return f(m['x'], prefix)
    else:
        m = pm.match(pm.Cons(pm.Star('head'), pm.Star('tail'))).attempt_match(expr)
        assert m is not None
        mapped_tail = []
        for x in m['tail']:
            mapped_tail.append(expr_map_literals(f, x, prefix + [m['head']]))
        return tuple([m['head']] + mapped_tail)


def identity(x):
    return x


def match_user_macro_body(f):
    return pm.match(
        ('user_macro', pm.Star('name'), pm.Star('params'),
            pm.Cons('body', pm.Star('statements')))
        ).replace(f)


@match_user_macro_body
def get_macro_param_names(name, params, statements):
    match_params = pm.match(pm.Cons('parameters', pm.Star('p')))
    m = match_params.attempt_match(params)
    assert m
    return m['p']


@match_user_macro_body
def get_macro_statements(name, params, statements):
    return statements


# wrap macro body in env_begin / env_end pairs
@match_user_macro_body
def wrap_body_in_env_rule(name, params, statements):
    statements_prime = [('env_begin',)] + statements + [('env_end',)]
    return ('user_macro', name, params, BODY(*statements_prime))


@match_user_macro_body
def allocate_locals_rule(name, params, statements):
    f = pm.match((LOCAL(pm.Star('x')),)).replace(lambda x : (
            ('env_declare', L(x)),
            ('env_set', L(x), ('allocate_local', )),
            ('free_local_on_env_exit', ('env_get', L(x))),
        ))
    statements_prime = []
    for expr in statements:
        statements_prime += list(f([expr]))
    return ('user_macro', name, params, BODY(*statements_prime))


@match_user_macro_body
def expand_while_block_rule(name, params, statements):
    def rewrite_while_block(x, statements):
        return tuple(
            [BEGIN_LOOP(x)] +
            statements +
            [END_LOOP(x)]
        )
    f = (pm.match(
            (('while', ARGS(pm.Star('x')), pm.Cons('body', pm.Star('statements'))), )
        ).replace(rewrite_while_block))
    statements_prime = []
    for expr in statements:
        statements_prime += list(f([expr]))
    return ('user_macro', name, params, BODY(*statements_prime))

@match_user_macro_body
def expand_if_block_rule(name, params, statements):
    def rewrite_if_block(x, statements):
        t = HIDDEN('if_tmp')
        return tuple(
            [('env_begin', ),
            LOCAL(t),
            COPY(x, t),
            BEGIN_LOOP(t), ] +
            statements +
            [CLEAR(t),
            END_LOOP(t),
            ('env_end', ), ]
        )
    f = (pm.match(
            (('if', ARGS(pm.Star('x')), pm.Cons('body', pm.Star('statements'))), )
        ).replace(rewrite_if_block))
    statements_prime = []
    for expr in statements:
        statements_prime += list(f([expr]))
    return ('user_macro', name, params, BODY(*statements_prime))

def expand_macro_call(macro, substitutions):
    def rewrite_literal(x, prefix):
        # XXX todo look at prefix, don't rewrite if it
        # containts 'constant' or something like that
        # (since that would indicate the literal L(x)
        # does not refer to a variable)
        l_x = L(x)
        if l_x in substitutions:
            return substitutions[l_x]
        else:
            return l_x

    @match_user_macro_body
    def rewrite_macro(name, params, statements):
        # extract parameter names
        match_params = pm.match(pm.Cons('parameters', pm.Star('p')))
        m = match_params.attempt_match(params)
        param_names = m['p']

        assert len(param_names) == len(substitutions)

        header = [('env_begin', )]
        for x in param_names:
            assert x in substitutions
            header += [
                ('env_declare', x),
                ('env_set', x, ('outer_env_get', substitutions[x])),
            ]

        footer = [('env_end', )]

        statements_prime = statements
        # for expr in statements:
        #     expr_prime = expr_map_literals(rewrite_literal, expr)
        #     statements_prime.append(expr_prime)
        statements_prime = header + statements_prime + footer
        params_prime = []
        return ('user_macro', name, params_prime, BODY(*statements_prime))

    return rewrite_macro(macro)


def make_expand_all_macro_calls_rule(user_macro_definitions):
    @match_user_macro_body
    def expand_all_macro_calls_rule(name, params, statements):

        def inline_macro(macro_name, args):
            """
            returns statments from expanded macro using given arguments
            """
            macro = user_macro_definitions[macro_name]
            params = get_macro_param_names(macro)
            assert len(args) == len(params)
            substitutions = dict(zip(params, args))
            expanded_macro = expand_macro_call(macro, substitutions)
            return get_macro_statements(expanded_macro)

        f = (pm.match(
                (
                    ('call_macro',
                        NAME(pm.Star('macro_name')),
                        pm.Cons('arguments',
                        pm.Star('args')),
                    ),
                )
            ).replace(inline_macro))
        
        statements_prime = []
        for expr in statements:
            statements_prime += list(f([expr]))
        return ('user_macro', name, params, BODY(*statements_prime))

    return expand_all_macro_calls_rule

def rewrite_macro_until_fixed_point(macro):
    transforms = {
        'allocate_locals' : allocate_locals_rule,
        'expand_while_block' : expand_while_block_rule,
        'expand_if_block' : expand_if_block_rule,
    }
    
    changed = True
    while changed:
        changed = False
        for transform_name in sorted(transforms):
            macro_out = transforms[transform_name](macro)
            changed = changed or (macro_out != macro)
            macro = macro_out
    return wrap_body_in_env_rule(macro)

def compile_macro(macro_defns, macro_name):
    rewritten_macros = {}
    for name in macro_defns:
        rewritten_macros[name] = rewrite_macro_until_fixed_point(macro_defns[name])
        print '>>> rewrote macro "%s"' % name
        expr_print(rewritten_macros[name])
    
    expand_all_macro_calls_rule = make_expand_all_macro_calls_rule(rewritten_macros)

    macro = rewritten_macros[macro_name]
    changed = True
    while changed:
        macro_out = expand_all_macro_calls_rule(macro)
        changed = (macro_out != macro)
        macro = macro_out
    print '>>> rewritten main macro:'
    expr_print(macro)
    return macro
