"""
brainfuck -> gnu ia32 assembly compiler.
"""

import sys

PROGRAM_START = r"""
.globl _start
_start:
    start:
    # for(int i = 0; i < 30000; ++i) buff[i] = 0
    subl	$30000,%esp
    movl        $0,%eax
zero_buff_start:
    cmpl        $30000,%eax
    je          zero_buff_end
    movb        $0,0(%esp,%eax,1)
    incl        %eax
    jmp         zero_buff_start
zero_buff_end:
    # initialise data pointer
    movl	$0,%eax
"""

WRITE_CHAR = r"""
    movl	%eax,%esi # save eax
    # write(stdout, &(buffer[eax]), 1)
    movl	%eax,%ecx
    addl	%esp,%ecx
    movl	$4,%eax
    movl	$1,%ebx
    movl	$1,%edx
    int		$0x80
    movl	%esi,%eax # restore eax
"""

READ_CHAR = r"""
    movl	%eax,%esi # save eax
    # read(stdin, &(buffer[eax]), 1)
    movl	%eax,%ecx
    addl	%esp,%ecx
    movl	$3,%eax
    movl	$0,%ebx
    movl	$1,%edx
    int		$0x80
    movl	%esi,%eax # restore eax
"""

DP_RIGHT = r"""
    incl        %eax
"""

DP_LEFT = r"""
    decl	%eax
"""

DP_INC = r"""
    incb	0(%esp, %eax, 1)
"""

DP_DEC = r"""
    decb	0(%esp, %eax, 1)
"""

BEGIN_WHILE = r"""
    movb	0(%esp, %eax, 1),%bl
    testb	%bl,%bl
    je		<END_LABEL>
<BEGIN_LABEL>:
"""

END_WHILE = r"""
    movb	0(%esp, %eax, 1),%bl
    testb	%bl,%bl
    jne		<BEGIN_LABEL>
<END_LABEL>:
"""

PROGRAM_END = r"""
    addl	$30000,%esp
    movl	$1,%eax
    movl	$0,%ebx
    int		$0x80
"""

def die(s):
    print s
    sys.exit(1)

def emit(s):
    print s

def compile(s):
    label_stack = []

    def begin_while():
        i = len(label_stack)
        label_stack.append(i)
        code = BEGIN_WHILE
        code = code.replace('<END_LABEL>', 'end_%d' % i)
        code = code.replace('<BEGIN_LABEL>', 'begin_%d' % i)
        return code

    def end_while():
        if not label_stack:
            die('error: encountered "]" without matching "["')
        i = label_stack.pop()
        code = END_WHILE
        code = code.replace('<END_LABEL>', 'end_%d' % i)
        code = code.replace('<BEGIN_LABEL>', 'begin_%d' % i)
        return code

    code_generator = {
        '<' : lambda : DP_LEFT,
        '>' : lambda : DP_RIGHT,
        '+' : lambda : DP_INC,
        '-' : lambda : DP_DEC,
        '[' : begin_while,
        ']' : end_while,
        '.' : lambda : WRITE_CHAR,
        ',' : lambda : READ_CHAR,
    }
    emit(PROGRAM_START)
    for c in s:
        if c in code_generator:
            emit(code_generator[c]())
        else:
            pass # ignore unrecognised characters
    emit(PROGRAM_END)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as source_file:
        s = '\n'.join(source_file.readlines())
    compile(s)
