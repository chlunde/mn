#!/usr/bin/env python
# Color pair management for curses in Python

import curses

# Ported from tmux/colours.c

term_table = None

def color_rgb_distance(rgb1, rgb2):
    """Squared error loss"""
    return sum(map(lambda v: (v[0]-v[1])**2, zip(rgb1,rgb2)))

def color_hex_find(hx):
    rgb = tuple([int(hx[i:i+2], 16) for i in (0,2,4)])
    return color_rgb_find(rgb)

def color_rgb_find(rgb):
    global term_table
    if term_table is None:
        term_table = create_term_table()
    
    lowest = 2**32
    for i, rgb2 in enumerate(term_table):
	distance = color_rgb_distance(rgb, rgb2)
	if distance < lowest:
	    lowest = distance
	    color = i
    
    return color

# rgb -> xterm color
def create_term_table():
    l = [(-1,-1,-1)] * 256

    r, g, b = 0, 0, 0
    for i in range(240, 24, -1):
	rv, gv, bv = 0, 0, 0
	if r != 0:
	    rv = (r * 40) + 55;
	if g != 0:
	    gv = (g * 40) + 55;
	if b != 0:
	    bv = (b * 40) + 55;

	l[256 - i] = (rv, gv, bv)

	b += 1

	if b > 5:
	    b = 0
	    g += 1

	if g > 5:
	    g = 0
	    r += 1

    for i in range(24, 0, -1):
	v = 8 + (24 - i) * 10;
	l[256 - i] = (v, v, v)

    return l

reserved_pairs = 1
pairs = dict()

def get_pair_no(fg, bg="#000000"):
    if fg.startswith("#"):
        fg = color_hex_find(fg[1:])
    if bg.startswith("#"):
        bg = color_hex_find(bg[1:])

    pair = (fg,bg)
    if not pair in pairs:
        pair_no = len(pairs) + reserved_pairs
        curses.init_pair(pair_no, fg, bg)
        pairs[pair] = pair_no

    return pairs[pair]
 #   return pairs[pair], fg, bg, term_table[fg], term_table[bg]

def get_pair(fg, bg="#000000"):
    return curses.color_pair(get_pair_no(fg, bg))

# vim: sw=4:sts=4:foldmethod=marker:foldlevel=0:foldmarker=def,return:expandtab
