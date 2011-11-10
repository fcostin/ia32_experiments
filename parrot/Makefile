# n.b. build-id=none prevents the generated object file
# being tagged with a .note.gnu.build-id section
GCC_OPTS := -nostdlib -Wl,--build-id=none

all:	a.out
	./a.out
.PHONY: all

clean:
	rm -f a.out
.PHONY: clean

a.out:	parrot.s
	gcc $< $(GCC_OPTS) -o $@

dis:	a.out
	objdump -D ./a.out | less
.PHONY: dis
