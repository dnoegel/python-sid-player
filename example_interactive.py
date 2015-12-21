#!/usr/bin/env python2
# coding:utf-8

import gobject
import termios
import fcntl
import sys
import os

from sidplay.Player import SidBackend

"""
Example of how to use the SID player in an interactive way
"""


class Player(SidBackend):
    """
    Simple domain wrapper around the orginal SidBackend
    This one may also contain more specific logic like "play next file"
    """
    NEXT = 1
    PREV = -1

    def play_from_listing(self, delta):
        self.stop()
        current_file = self.get_file()
        dir = os.path.dirname(current_file)
        file_name = os.path.basename(current_file)
        all_files = sorted(os.listdir(dir))

        position = all_files.index(file_name)
        next = position + delta
        if len(all_files) < next + delta:
            next = 0
        if next < 0:
            next = len(all_files) - 1

        next_file = os.path.join(dir, all_files[next])

        self.play(next_file)


class Terminal:
    """Takes care of configuring the terminal to our needs (interactive even with gobject main loop)"""

    def setup(self):
        """Prepare the current terminal for our needs"""

        self.fd = sys.stdin.fileno()

        self.oldterm = termios.tcgetattr(self.fd)
        newattr = termios.tcgetattr(self.fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSANOW, newattr)

        self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)

    def destroy(self):
        """Reset the terminal to the previous default"""

        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)


if __name__ == "__main__":

    # Enforce file name
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)
    file = sys.argv[1]

    # Play the sid file
    app = Player({
        'mos8580': True
    })
    app.play(file)

    # Start the gobject loop that gstreamer needs
    loop = gobject.MainLoop()
    gobject.threads_init()
    context = loop.get_context()

    # Prepare the terminal
    terminal = Terminal()
    terminal.setup()
    context.iteration(True)

    # Main loop - read input from terminal
    try:
        while 1:
            try:
                c = sys.stdin.read(1)

                if c == ' ':
                    app.play_pause()
                if c == '+':
                    app.change_speed(0.1)
                if c == '-':
                    app.change_speed(-0.1)
                if c == 'n':
                    app.play_from_listing(app.NEXT)
                if c == 'p':
                    app.play_from_listing(app.PREV)
                if c == 's':
                    app.seek(10)
            except IOError:
                pass
    except KeyboardInterrupt:
        print "Exiting…"

    # Reset the terminal
    terminal.destroy()
