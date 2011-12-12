"""
renders brainfuck programs as giant square bitmaps of opcode glyphs
"""

import Image
import sys
import math
import numpy

GLYPH_LEFT = 0
GLYPH_RIGHT = 1
GLYPH_INC = 2
GLYPH_DEC = 3
GLYPH_BEGIN_LOOP = 4
GLYPH_END_LOOP = 5
GLYPH_GET_CHAR = 6
GLYPH_PUT_CHAR = 7
GLYPH_NONE = 8

CODE_TO_GLYPH = {
    '<' : GLYPH_LEFT,
    '>' : GLYPH_RIGHT,
    '+' : GLYPH_INC,
    '-' : GLYPH_DEC,
    '[' : GLYPH_BEGIN_LOOP,
    ']' : GLYPH_END_LOOP,
    ',' : GLYPH_GET_CHAR,
    '.' : GLYPH_PUT_CHAR,
}


BITMAP_LEFT = """
....*
..**.
**...
..**.
....*
"""

BITMAP_RIGHT = """
*....
.**..
...**
.**..
*....
"""

BITMAP_INC = """
..*..
..*..
*****
..*..
..*..
"""

BITMAP_DEC = """
.....
.....
*****
.....
.....
"""

BITMAP_BEGIN_LOOP = """
*****
**...
**...
**...
*****
"""

BITMAP_END_LOOP = """
*****
...**
...**
...**
*****
"""

BITMAP_PUT_CHAR = """
.....
.....
...**
...**
.....
"""

BITMAP_GET_CHAR = """
.....
...**
...**
....*
...*.
"""

BITMAP_NONE = """
.....
.....
.....
.....
.....
"""

GLYPH_TO_BITMAP = {
    GLYPH_LEFT : BITMAP_LEFT,
    GLYPH_RIGHT : BITMAP_RIGHT,
    GLYPH_INC : BITMAP_INC,
    GLYPH_DEC : BITMAP_DEC,
    GLYPH_BEGIN_LOOP : BITMAP_BEGIN_LOOP,
    GLYPH_END_LOOP : BITMAP_END_LOOP,
    GLYPH_GET_CHAR : BITMAP_GET_CHAR,
    GLYPH_PUT_CHAR : BITMAP_PUT_CHAR,
    GLYPH_NONE : BITMAP_NONE,
}

BITMAP_RAW_TILE_SIZE = 5
BITMAP_TILE_SIZE = BITMAP_RAW_TILE_SIZE + 1


def get_input_string(file_name):
    with open(file_name, 'r') as f:
        s = ''.join(f.readlines())
    return s.replace('\n', '')

def isqrt(n):
    return int(math.ceil(n ** 0.5))

def make_glyphmap(s):
    glyphs = [CODE_TO_GLYPH.get(c, GLYPH_NONE) for c in s]
    n = len(glyphs)
    r = isqrt(n)
    m = r * r
    padded_glyphs = glyphs + ([GLYPH_NONE] * (m - n))
    gmap = numpy.asarray(padded_glyphs, dtype = numpy.int)
    gmap = numpy.reshape(gmap, (r, r))
    return gmap

def make_tile(s):
    a = [c == '*' for c in s.replace('\n', '')]
    b = numpy.reshape(numpy.asarray(a, dtype = numpy.bool), (BITMAP_RAW_TILE_SIZE, ) * 2)
    c = numpy.zeros((BITMAP_TILE_SIZE, ) * 2, dtype = numpy.bool)
    c[:-1, :-1] = b
    return c

def make_bitmap(glyphmap):
    (m, n) = glyphmap.shape
    p = BITMAP_TILE_SIZE

    tiles = dict((k, make_tile(v)) for (k, v) in GLYPH_TO_BITMAP.iteritems())

    (q, r) = (m * p, n * p)
    bitmap = numpy.zeros((q, r), dtype = numpy.bool)
    for i in xrange(m):
        for j in xrange(n):
            bitmap[i * p : (i + 1) * p, j * p : (j + 1) * p] = tiles[glyphmap[i, j]]
    return bitmap

def save_bitmap(bitmap, file_name):
    rgba_shape = (bitmap.shape[0], bitmap.shape[1], 4)
    rgba_bitmap = numpy.zeros(rgba_shape, dtype = numpy.uint8)
    rgba_bitmap[:, :, 3] = 255
    for i in xrange(3):
        rgba_bitmap[:, :, i] = 255 * bitmap
    rgba_bitmap[:, :, :-1] = 255 - rgba_bitmap[:, :, :-1]
    im = Image.fromarray(rgba_bitmap)
    im.save(file_name)

def main():
    if len(sys.argv) != 3:
        print 'usage: in.bf out.png'
        sys.exit(1)
    s = get_input_string(sys.argv[1])
    glyphmap = make_glyphmap(s)
    bitmap = make_bitmap(glyphmap)
    save_bitmap(bitmap, sys.argv[2])

if __name__ == '__main__':
    main()
