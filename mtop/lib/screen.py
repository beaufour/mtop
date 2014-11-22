from __future__ import print_function
import fcntl
import os
import signal
import sys
import struct
import termios


class Screen(object):
    """
    Class that behaves like `curses`.

    NOTE: Would love to just use the standard python curses library,
    but I failed to handle terminal resizing properly (on Mac OS
    X). This interface is about the same as the curses screen one
    though, so it should be easy to swap in/out.
    """

    def __init__(self):
        signal.signal(signal.SIGWINCH, self._on_resize)

    def _on_resize(self, a, b):
        pass

    def end(self):
        print('\x1b[5l')

    def timeout(self, timeout):
        self._timeout = timeout / 1000

    def clear(self):
        print('\x1b[H\x1b[J',)
        sys.stdout.flush()

    def addstr(self, y, x, txt):
        print('\x1b[%d;%dH%s' % (y + 1, x, txt),)
        sys.stdout.flush()

    def getmaxyx(self):
        try:
            return int(os.environ["LINES"]), int(os.environ["COLUMNS"])
        except KeyError:
            height, width = struct.unpack("hhhh",
                                          fcntl.ioctl(0, termios.TIOCGWINSZ, "\000" * 8))[0:2]
        if not height:
            return 25, 80

        return height, width
