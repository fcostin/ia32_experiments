.data
hello:
	.string "hello world\n"

.text
.globl _start
_start:
	movl	$4,%eax # 4 is syscall write
	movl	$1,%ebx # 1 is file stdout
	movl	$hello,%ecx # string argument
	movl	$12,%edx # length of argument
	int		$0x80 # syscall
	movl	$1,%eax # 1 is syscall exit
	movl	$0,%ebx # return code 0
	int		$0x80 # syscall
