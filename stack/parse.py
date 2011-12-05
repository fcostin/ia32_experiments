def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

def parse_int(x):
    assert is_int(x)
    return ('constant', int(x))

def is_char(x):
    return len(x) == 3 and x[0] == '\'' and x[2] == '\''

def parse_char(x):
    assert is_char(x)
    return ('constant', ord(x[1]))

def is_word(x):
    if len(x) == 0:
        return False
    else:
        for c in x:
            if not (c.islower() or c == '_'):
                return False
        return True

def parse_word(x):
    assert is_word(x)
    return ('word', x)

def parse_token(x):
    if is_int(x):
        return parse_int(x)
    elif is_char(x):
        return parse_char(x)
    elif is_word(x):
        return parse_word(x)
    else:
        raise ValueError('unknown token: "%s"' % str(s))

def indentation_level(line):
    i = 0
    while (i < len(line)) and (line[i] == '\t'):
        i += 1
    return i

def parse_line(line):
    if not line.strip():
        return []
    else:
        level = indentation_level(line)
        tokens = line.split()
        return [(level, map(parse_token, tokens))]

def test():
    with open('test.txt', 'r') as f:
        for line in f:
            print parse_line(line)

if __name__ == '__main__':
    test()
