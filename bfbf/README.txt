beginnings of a self-hosting brainfuck compiler

currently sketching out the source for the compiler
in a stack based language implemented out of brainfuck
implemented as a python script

the idea is to largely express the brainfuck compiler
in this stack based language, then expand all the
definitions of the stack operators in terms of the
brainfuck (including the huge code blocks to emit
the gnu ia32 assembly code) into a pure brainfuck
script.

ISSUES:
	- nothing has been tested
	- implementation of [ & ] is missing
