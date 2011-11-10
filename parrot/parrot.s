# read a character from stdin and parrot it back
# surrounded by some fluff
.data
header:
	.string "i got : '"
footer:
	.string "'\n"
.globl _start
_start:
	subl	$1,%esp # grow stack 1 byte
	# eax = read(stdin, stack, 1);
	movl	$3,%eax # syscall 3 : read
	movl	$0,%ebx # file 0 : stdin
	movl	%esp,%ecx
	movl	$1,%edx
	int		$0x80 # syscall
	# eax = write(stdout, header, strlen(header));
	movl	$4,%eax
	movl	$1,%ebx
	movl	$header,%ecx
	movl	$9,%edx
	int		$0x80
	# eax = write(stdout, stack, 1);
	movl	$4,%eax
	movl	$1,%ebx
	movl	%esp,%ecx
	movl	$1,%edx
	int		$0x80
	# eax = write(stdout, footer, strlen(footer));
	movl	$4,%eax
	movl	$1,%ebx
	movl	$footer,%ecx
	movl	$2,%edx
	int		$0x80
	addl	$1,%esp # shrink stack 1 byte
	# exit(0);
	movl	$1,%eax
	movl	$0,%ebx
	int		$0x80
