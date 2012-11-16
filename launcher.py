import curses
import curses.ascii
import os
import sys

def d(a, b):
    score, pos = 0.0, 0
    ms = []
    for y in a:
        match = False
        for i,x in enumerate(b[pos:]):
            if y.upper() == x.upper():
                match = True
                pos += i + 1
                score += 1.0 / (i + 1)
                ms.append(pos - 1)
                break
        if not match: return None
    if score == 0: return None
    return { 'return': b, 'hits': ms, 'score': score }

def pr(y, x, s, p=3, b=False):
    attr = curses.color_pair(p)
    if b: attr |= curses.A_BOLD
    screen.addstr(y, x, s, attr)

def match(string):
    screen.clear()
    r = sorted([d(string, z) for z in data if d(string, z)], key = lambda x: x['score'])
    for i, x in enumerate(reversed(r)):
        if i > h - 4: break
        pr(2+i, 1, "%.3f" % x['score'], 1, True)
        for j, y in enumerate(x['return']):
            if j >= w - 4: break
            if j in x['hits']:
                pr(2+i, 8+j, y, 2, True)
            else:
                pr(2+i, 8+j, y)
    try:
        return r[-1]['return']
    except:
        return []

screen = curses.initscr()
curses.start_color()

curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_CYAN,  curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

screen.keypad(1)
curses.noecho()
curses.cbreak()

prompt = ">> "
y, x = 0, len(prompt) + 1
h, w = screen.getmaxyx()
w = w - x - 1
string = ""
pos = 0
out = ""

data = open("input.txt", "r").read().splitlines()

try:
    while True:
        pr(y, x, string)
        pr(y, 1, prompt, 3, True)
        screen.move(y, x + pos)
        ch = screen.getch()
        if   ch == 27: break
        elif ch == 5:  pos = len(string)
        elif ch == 1:  pos = 0
        elif ch == 32: pass
        elif ch == 10: break
        elif ch == 9:  
            out = string; 
            break
        elif ch == 263:
            if pos > 0:
                string = string[0:-1]
                pos -= 1
                pr(y, x+pos, " ")
                out = match(string)
        elif ch == 23:
            screen.clear()
            pos = 0
            string = ""
        elif curses.ascii.isprint(ch):
            if len(string) < w:
                string = string[:pos] + chr(ch) + string[pos:]
                pos += 1
                out = match(string)
finally:
    curses.endwin()

print(out)
