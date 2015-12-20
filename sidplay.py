#!/usr/bin/env python2
# coding:utf-8

import pygst

pygst.require("0.10")
import gst
import gobject
import termios, fcntl, sys, os

class SidBackend():
    """SidPlay plays given SID tune files and allows (un)pausing and speeding up SID tunes
    """

    def __init__(self):
        self.build_pipleine()

    def play(self, file, tune=0):
        """Play the given TUNE of given file FILE

        :param file: The SID file to play
        :param tune: The SID tune inside the file
        """
        self.pipeline.set_state(gst.STATE_READY)

        self.reset_siddec()

        self.audiosrc.set_property('location', file)
        self.siddec.set_property('tune', tune)
        self.pipeline.set_state(gst.STATE_PLAYING)
        print "Will now playing", self.audiosrc.get_property('location')

    def reset_siddec(self):
        """Resets the siddec element due to issues

        It seems the siddec element cannot handle changes in the filesrc's location property.
        It will keep playing the previous audio.
        This workaround will remove it from the pipe and re-add a new siddec element.
        Additional resource for this topic:
            http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-dynamic-pipelines.html
        """
        self.siddec.set_state(gst.STATE_NULL)
        self.pipeline.remove(self.siddec)
        self.siddec = gst.element_factory_make("siddec", "siddec")
        self.pipeline.add(self.siddec)
        gst.element_link_many(self.audiosrc, self.siddec, self.queue)

    def stop(self):
        self.pipeline.set_state(gst.STATE_NULL)

    def play_pause(self):
        """Play / pause the playback depending on the current status"""

        should_pause = gst.STATE_PLAYING in self.pipeline.get_state()

        if should_pause:
            self.pipeline.set_state(gst.STATE_PAUSED)
        else:
            self.pipeline.set_state(gst.STATE_PLAYING)

    def change_speed(self, delta):
        """Change the speed by DELTA

        :param delta: How to change current playback speed?
        """

        value = self.speed.get_property('speed') + delta
        self.speed.set_property('speed', value)
        print "Changed speed to %", value

    def get_file(self):
        return self.audiosrc.get_property('location')

    def build_pipleine(self):
        """Internal helper to build the gstreamer pipleine"""

        self.pipeline = gst.Pipeline("sidplay-pipeline")

        self.audiosrc = gst.element_factory_make("filesrc", "audio")
        self.siddec = gst.element_factory_make('siddec', 'siddec')
        self.queue = gst.element_factory_make('queue', 'queue')
        self.speed = gst.element_factory_make('speed', 'speed')
        self.sink = gst.element_factory_make("autoaudiosink", "sink")

        self.pipeline.add_many(self.audiosrc, self.siddec, self.queue, self.speed, self.sink)
        gst.element_link_many(self.audiosrc, self.siddec, self.queue, self.speed, self.sink)

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


class Player(SidBackend):
    """
    Simple domain wrapper around the orginal SidBackend
    This one may also contain more specific logic like "play next file"
    """
    NEXT = 1
    PREV = -1

    def __init__(self):
        SidBackend.__init__(self)

    def play_from_listing(self, delta):
        self.stop()
        current_file = self.get_file()
        dir = os.path.dirname(current_file)
        file_name = os.path.basename(current_file)
        all_files =  sorted(os.listdir(dir))

        position = all_files.index(file_name)
        next = position + delta
        if len(all_files) < next + delta:
            next = 0
        if next < 0:
            next = len(all_files)-1


        next_file = os.path.join(dir, all_files[next])

        self.play(next_file)


if __name__ == "__main__":

    # Enforce file name
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)
    file = sys.argv[1]

    # Play the sid file
    app = Player()
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
            except IOError:
                pass
    except KeyboardInterrupt:
        print "Exiting…"

    # Reset the terminal
    terminal.destroy()
