rfc nov 17th 2011


Contents
--------

div10.bf.plan	:	initial plan outlining how to kludge
					together a divide by 10 program

divide_ten.py	:	python scipt writing brainfuck
					program for divide by 10 to
					standard output

div10.bf		:	test of routine, using output
					from divide_ten.py


Why?
----

For use as sub-component in program to print integer values to stdout.

Why?
----

So the compiler can emit code containing integer constants determined
at compile time.

Why?
----

A. So, in combination with the detection of strings of repeated
brainfuck opcodes, terser assembly can be emitted. For example,
instead of emitting code to increment the same byte 100 times,
we could add the integer constant 100 to that byte. Similarly
for decrements, left moves, right moves.

B. So the compiler can use compile-time integers in the unique
labels inserted into the output assembly, which is arguably
less bizzare than strings of Ws.

Is it any good?
---------------

Yes.
