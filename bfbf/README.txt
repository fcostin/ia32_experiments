a self-hosting brainfuck to gnu ia32 assembly compiler.

The idea is to largely express the brainfuck compiler
in this stack based language, then expand all the
definitions of the stack operators in terms of the
brainfuck (including the huge code blocks to emit
strings of gnu ia32 assembly code) into a pure
brainfuck script.

contents:
	compile.py		:	bf to gnu ia32 assembly compiler, in python
	bf_interp.py	:	a bf interpreter, in python, to aid debugging of bf programs
	braintease.py	:	generates bf code for bf to gnu ia32 assembly compiler
	Makefile		:	bootstraps brainfuck compiler into existence, tests it by compiling hello.brainfuck


rfc, 13th nov 2011
