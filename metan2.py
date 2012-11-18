#!/usr/bin/env python
import curses
import curses.ascii
import termcolors
import os

# TODO: This Matcher code has bugs...

class Matcher(object):
    def __init__(self, choices):
        self.choices = [(0, choice, choice.lower(), [(True, len(choice))])
                        for choice in choices]
        self.last_matches = self.choices
        self.last_string = ""

    def match(self, s):
        s = s.lower()
        if s == "":
            return self.choices

        # Build a list of tuples (distance, choice, matches)
        # matches is a list of tuples with matched/skipped substrings in choice
        if s.startswith(self.last_string):
            searchspace = self.last_matches
        else:
            searchspace = self.choices

        l = []
        ls = len(s)

        for score, choice_org, choice, desc in searchspace:
            lc = len(choice)

            # Restore saved state, if any.  I.e. the state for current
            # search minus last character

            # The last attempt can be improved, so remove it
            # and calculate the previous ci, si
            while len(desc) and desc[-1][0]:
                desc = desc[:-1]

            desc = desc[:]

            ci = sum([mlen for _, mlen in desc])
            si = sum([mlen for skipped, mlen in desc if not skipped])

            while si < ls and ci < lc:
                # Matching
                mlen = 0
                while si < ls and ci < lc and s[si] == choice[ci]:
                    ci += 1
                    si += 1
                    mlen += 1

                if mlen:
                    if len(desc) and desc[-1][0] is False:
                        desc[-1] = (False, desc[-1][1] + mlen)
                    else:
                        desc.append((False, mlen))

                if si >= ls or ci >= lc:
                    break

                # Skip to next match
                cnext = choice.find(s[si], ci)
                if cnext == -1:
                    break

                mlen = cnext - ci
                ci += mlen

                desc.append((True, mlen))

            score = sum([mlen for skipped, mlen in desc if not skipped])
            score -= sum([min(mlen * .2, .5) for skipped, mlen in desc[1:] if skipped])
            leftover = len(choice) - sum([mlen for _, mlen in desc])
            if leftover:
                desc.append((True, leftover))
            else:
                # Bonus score if we can anchor the search to the end
                score += 0.1

            # Severe penalty for leftovers in search string
            if si != ls:
                score /= (1 + ls - si)

            if score > 0:
                l.append((score, choice_org, choice, desc))
        self.last_matches = list(reversed(sorted(l)))
        self.last_string = s

        return self.last_matches


class MetaN(object):
    def __init__(self, stdscr):
        self.scr = stdscr
        curses.start_color()
        self.scr.keypad(True)
        self.scr.nodelay(True)
        curses.raw()
        self.cmd = ""
        self.cmd_cursor = 0

        self.cmd_history_cursor = 0
        self.cmd_history = []

        self.choices = []
        self.matches = []

        self.statusbar = ""

        self.PROMPT = termcolors.get_pair("#AE81FF")
        self.PROMPT_INPUT = termcolors.get_pair("#FFFFFF") | curses.A_BOLD
        self.CHOICE_MATCHED = termcolors.get_pair("#66D9EF") | curses.A_BOLD | curses.A_UNDERLINE
        self.CHOICE_SKIPPED = termcolors.get_pair("#66D9EF")
        self.CHOICE = termcolors.get_pair("#F92672")
        self.SELECTION = termcolors.get_pair("#F92672", "#49483E") | curses.A_UNDERLINE
        self.SELECTED = termcolors.get_pair("#F92672", "#49483E")
        self.STATUSBAR = termcolors.get_pair("#F92672", "#49483E")

        self.selection = 0
        self.selected = []
        self.word_at_selection = ""
        self.done = False
        self.dirty = True

    def paint(self):
        h, w = self.scr.getmaxyx()

        if not self.dirty:
            return

        self.matches = self.matcher.match(self.cmd)
        self.dirty = False

        self.scr.move(0, 0)
        self.scr.clrtobot()

        prompt = ">> "
        self.scr.addstr(0, 0, prompt, self.PROMPT)
        self.scr.addstr(self.cmd, self.PROMPT_INPUT)
        #self.scr.clrtoeol()  # after backspace

        y = 1

        unseen_selections = self.selected[:]  # clone

        def tail_length():
            if len(unseen_selections):
                return min(2 + len(unseen_selections), 5)
            return 1

        dy = 0  # for len(self.matches) == 0, so we can use dy outside the loop
        for dy, (score, choice, _, desc) in enumerate(self.matches):
            if (y + dy + tail_length()) >= h:
                break

            self.scr.move(y + dy, 0)
            attrs = 0
            string = "%.2f " % score
            if choice in self.selected:
                string = " ~~  "
                attrs = self.SELECTED
                unseen_selections.remove(choice)

            if dy == self.selection:
                attrs = self.SELECTION

            self.scr.addstr(string, attrs)

            x = 5
            offset = 0
            for i, (skipped, slen) in enumerate(desc):
                if x >= w - 2:
                    break

                # TODO: Verify
                if slen >= w - x - 1:
                    slen = w - x - 2
                x += slen

                if (i == 0 or i == len(desc) - 1) and skipped:
                    # not inbetween matched characters (first or last)
                    color = self.CHOICE
                elif skipped:
                    color = self.CHOICE_SKIPPED
                else:
                    color = self.CHOICE_MATCHED
                self.scr.addstr(choice[offset:offset + slen], color)

                if dy == self.selection and not skipped:
                    # TODO: Assumes cursors is at the end of the line
                    self.word_at_selection = choice[offset:offset + slen]

                offset += slen

            #self.scr.clrtoeol()

        y += dy

        #self.scr.clrtobot()
        if len(unseen_selections):
            #y += 1
            x = 5

            for dy, choice in enumerate(unseen_selections):
                self.scr.addstr(y + dy + 1, 0, " ~~   " + choice[0:w - x - 2], self.CHOICE)
                if y + dy + 3 >= h:
                    break
                #self.scr.clrtoeol()

            if dy == len(unseen_selections) - 1:
                self.scr.addstr(y, 0, "..also selected")
            else:
                self.scr.addstr(y, 0, "..also selected these and %d others" % (len(unseen_selections) - dy - 1))
            #self.scr.clrtoeol()

        self.scr.addstr(h - 1, 0, self.statusbar, self.STATUSBAR)
        # TODO: May fail if input is too long
        self.scr.move(0, len(prompt) + self.cmd_cursor)
        self.scr.refresh()

    def set_choices(self, l):
        self.all = l
        self.matcher = Matcher(l)
        self.matcher.match(self.cmd)
        self.dirty = True

    def add_choices(self, l):
        # TODO: Reuse matcher object and keep state
        # TODO: Keep cursor stable?
        self.set_choices(self.all + l)

    def load_cmd_history(self):
        f = open(os.path.expanduser("~/.launcher_history"), "r")
        self.cmd_history = f.read().splitlines()
        f.close()
        if not self.cmd_history_cursor:
            self.cmd_history_cursor = min(0, len(self.cmd_history) - 1)

    def save_cmd_history(self):
        f = open(os.path.expanduser("~/.launcher_history"), "a")
        f.write("\n".join(self.selected + [self.cmd]) + "\n")
        f.close()

    def handle_key(self):
        c = self.scr.getch()

        if c != -1:
            self.dirty = True

        # C('u') character code for Ctrl-u
        def C(a):
            return ord(a) & 31

        if c == -1:
            pass

        elif curses.ascii.isprint(c):
            self.cmd = self.cmd[0:self.cmd_cursor] + chr(c) + self.cmd[self.cmd_cursor:]
            self.cmd_cursor += 1

        elif c in (127, curses.KEY_BACKSPACE):
            if self.cmd_cursor:
                self.cmd = self.cmd[0:self.cmd_cursor - 1] + self.cmd[self.cmd_cursor:]
                self.cmd_cursor -= 1

        elif c == C('a'):
            self.cmd_cursor = 0

        elif c == C('c'):
            raise KeyboardInterrupt

        elif c == C('e'):
            self.cmd_cursor = len(self.cmd)

        elif c == C('k'):
            self.cmd = self.cmd[:self.cmd_cursor]

        elif c == C('l'):
            self.dirty = True
            # TODO: Check for input on stdin?

            # TODO: Hack to test history without leaving
            self.save_cmd_history()

        elif c == C('r'):
            self.load_cmd_history()
            if len(self.cmd_history):
                if self.cmd_history_cursor:
                    self.cmd_history_cursor -= 1
                else:
                    self.cmd_history_cursor = len(self.cmd_history) - 1
                self.cmd = self.cmd_history[self.cmd_history_cursor]
                self.cmd_cursor = len(self.cmd)

        elif c == C('s'):
            self.load_cmd_history()
            if len(self.cmd_history):
                self.cmd_history_cursor += 1
                self.cmd_history_cursor %= len(self.cmd_history)
                self.cmd = self.cmd_history[self.cmd_history_cursor]
                self.cmd_cursor = len(self.cmd)

        elif c == C('u'):
            self.cmd = self.cmd[self.cmd_cursor:]
            self.cmd_cursor = 0

        elif c == C('w'):
            # TODO: Assumes cursor is at end of line
            self.cmd = self.cmd[:-len(self.word_at_selection)]
            self.cmd_cursor = len(self.cmd)
            #self.cmd += "was: " + self.word_at_selection

        elif c == C('z'):
            choice = self.matches[self.selection][1]
            if not choice in self.selected:
                self.selected.append(choice)
            else:
                self.selected.remove(choice)

        elif c == 258:  # <Down>
            if self.selection < len(self.matches) - 1:
                self.selection += 1

        elif c == 259:  # <Up>
            if self.selection > 0:
                self.selection -= 1

        elif c == 260:  # <Left>
            if self.cmd_cursor:
                self.cmd_cursor -= 1

        elif c == 261:  # <Right>
            if self.cmd_cursor < len(self.cmd):
                self.cmd_cursor += 1

        elif c == 10:
            choice = self.matches[self.selection][1]
            if not choice in self.selected:
                self.selected.append(choice)
            self.done = True
            self.save_cmd_history()

        else:
            # TODO: Remove
            try:
                s = chr(c)
            except:
                s = "???"
            self.cmd += "[Unknown %d <%s>]" % (c, s)

        self.paint()


def main(stdscr, options, args):
    import select
    import fcntl

    # make stdin a non-blocking file
    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    choices = sys.stdin.read().splitlines()

    mn = MetaN(stdscr)

    mn.set_choices(choices)
    eof = False

    while not mn.done:
        mn.handle_key()

        rlist, wlist, xlist = select.select([sys.stdin, 0], [], [], 1/33.0)

        if sys.stdin in rlist:
            new_choices = []
            while True:
                try:
                    data = sys.stdin.readline()
                except IOError, e:
                    break

                if data == "":
                    eof = True
                    break

                new_choices.append(data.strip())

            mn.statusbar = "Adding %d choices" % len(new_choices)
            mn.add_choices(new_choices)
            mn.dirty = True
            mn.paint()

    return mn.selected

if __name__ == "__main__":
    from optparse import OptionParser
    import os
    import sys

    usage = """usage: %prog [options] [exec exec-args {} exec-args]

    Options are read from standard input by default, so for example
    
        ls -1 *.c | %prog -- ls -l

    will execute ls -l on the selected files.

    It is recommened to alias %prog to something shorter such av `mn'.

EXAMPLES:

    List all log files, pick some of them in %prog, and compress them as root with gzip:

    ls -1 *.log | %prog --print0 | xargs -0 sudo gzip -v

    """

    parser = OptionParser(usage=usage)
    parser.add_option("--print0", action="store_const", const="0", dest="output", default=None,
                      help="Print results on standard output.  Each option is followed by a ASCII NUL")
    parser.add_option("--print", action="store_const", const="n", dest="output",
                      help="Print results on standard output.  Each option is followed by a ASCII newline")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    # stdin and stdout may be pipes, clone them and
    # make pythons sys.stdin/stdout point to the pipes
    stdin_fileno = os.dup(0)
    stdout_fileno = os.dup(1)

    sys.stdin = os.fdopen(stdin_fileno, "r")
    sys.stdout = os.fdopen(stdout_fileno, "w")

    # For curses to work properly make sure fd 0/1 points
    # to the TTY
    f = open("/dev/tty", "r")
    os.dup2(f.fileno(), 0)
    f = open("/dev/tty", "w")
    os.dup2(f.fileno(), 1)

    selected = curses.wrapper(lambda x: main(x, options, args))

    if options.output == 'n':
        for a in selected:
            sys.stdout.write(a)
            sys.stdout.write('\n')
    elif options.output == '0':
        for a in selected:
            sys.stdout.write(a)
            sys.stdout.write('\0')
    else:
        params = args

        try:
            insert = params.index('{}')
            params = params[0:insert] + selected + params[insert + 1:]
        except ValueError:  # No {}
            params = params + selected

        os.execvp(args[0], params)

# vim: sw=4 sts=4 et
