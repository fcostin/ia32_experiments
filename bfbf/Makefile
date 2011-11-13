GCC_OPTS := -nostdlib -Wl,--build-id=none


all: hello.out check_fixed_point
	./hello.out
.PHONY: all

check_fixed_point: bf_compiler_self_hosted.s bf_compiler_self_hosted_2.s
	diff bf_compiler_self_hosted.s bf_compiler_self_hosted_2.s
.PHONY: check_fixed_point


clean:
	rm -f bf_compiler.brainfuck
	rm -f bf_compiler_boot.s
	rm -f bf_compiler_boot.out
	rm -f bf_compiler_self_hosted.s
	rm -f bf_compiler_self_hosted_2.s
	rm -f bf_compiler_self_hosted.out
	rm -f hello.s
	rm -f hello.out
	rm -f *.pyc
.PHONY: clean

bf_compiler.brainfuck:	braintease.py
	python $< > $@

bf_compiler_boot.s:	bf_compiler.brainfuck
	python compile.py $< > $@

bf_compiler_boot.out:	bf_compiler_boot.s
	gcc $< $(GCC_OPTS) -o $@

bf_compiler_self_hosted.s:	bf_compiler_boot.out bf_compiler.brainfuck
	cat bf_compiler.brainfuck | ./$< > $@

bf_compiler_self_hosted.out:	bf_compiler_self_hosted.s
	gcc $< $(GCC_OPTS) -o $@

bf_compiler_self_hosted_2.s:	bf_compiler_self_hosted.out bf_compiler.brainfuck
	cat bf_compiler.brainfuck | ./$< > $@

hello.s:	bf_compiler_self_hosted.out hello.brainfuck
	cat hello.brainfuck | ./$< > $@

hello.out:	hello.s
	gcc $< $(GCC_OPTS) -o $@
