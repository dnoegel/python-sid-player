#!/usr/bin/env python2
# coding:utf-8

import gobject

from sidplay.Player import SidBackend

"""
The simplest implementation of the SID player
"""


if __name__ == "__main__":

    # Enforce file name
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)
    file = sys.argv[1]

    # Play the sid file
    app = SidBackend()
    app.play(file)

    gobject.MainLoop().run()


