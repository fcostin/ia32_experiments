clear = lambda : '[-]'

dupe = lambda : '>' + clear() + '>' + clear() + '<<[->+>+<<]>>[-<<+>>]<'

move_right = lambda : '[->+<]>'

move_left = lambda : '[-<+>]<'

dec_if_positive = lambda : '>' + clear() + '<[' + move_right() + '-<]>' + move_left()

greater_than = lambda x : dec_if_positive() * x

def divide(x):
    return ''.join((
        divide_entry(),
        '[',
            divide_body(x),
        ']',
        divide_exit(),
    ))

divide_entry = lambda : move_right() + '>' + clear() + '+'
divide_exit = lambda : '<'

def divide_body(x):
    return ''.join((
        '<', dupe(),
        greater_than(x - 1),
        '>', clear(), '<',
        '[',
        '<',
        '-' * x,
        '<+',
        '>>>+<', clear(),
        ']',
        '>', move_left(),
    ))

if __name__ == '__main__':
    print divide(10)

