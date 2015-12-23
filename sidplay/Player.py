#!/usr/bin/env python2
# coding:utf-8

import pygst

pygst.require("0.10")
import gst

from threading import Timer
import time


class SidBackend():
    """SidPlay plays given SID tune files and allows (un)pausing and speeding up SID tunes
    """

    def __init__(self, sid_config={}):
        self.__build_pipleine()
        self.sid_config = sid_config

        self.current_song = None
        self.current_tune = 0
        self.current_length = 0

        self.__playback_start_time = 0

    def get_time(self):
        return time.time() - self.__playback_start_time

    def play(self, file, tune=0, length=0):
        """Play the given TUNE of given file FILE

        :param file: The SID file to play
        :param tune: The SID tune inside the file
        """
        self.pipeline.set_state(gst.STATE_READY)

        self.__reset_siddec()

        self.audiosrc.set_property('location', file)
        self.siddec.set_property('tune', tune)

        for key in self.sid_config:
            self.siddec.set_property(key, self.sid_config[key])

        self.__playback_start_time = time.time()
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.current_song = file
        self.current_tune = tune
        self.current_length = length

    def seek(self, seconds, from_start=False):
        """Siddec does not support seeking, so we need to emulate it"""

        speed_up = 40  # this is the internal speed up factor

        if from_start:
            song, tune, length = self.current_song, self.current_tune, self.current_length
            self.stop()
            self.play(song, tune, length)

        self.__playback_start_time -= seconds - (seconds * 1.0 / speed_up)
        self.volume.set_property('mute', True)  # mute, so we don't head the speed up
        self.speed.set_property('speed', speed_up)



        # Set timer, so we can stop the speed
        Timer(seconds * 1.0 / speed_up, self.__stop_seek).start()

    def stop(self):
        self.current_tune = 0
        self.current_song = None
        self.current_length = 0
        self.__playback_start_time = 0
        self.pipeline.set_state(gst.STATE_NULL)

    def play_pause(self):
        """Play / pause the playback depending on the current status"""

        should_pause = gst.STATE_PLAYING in self.pipeline.get_state()

        if should_pause:
            self.pipeline.set_state(gst.STATE_PAUSED)
        else:
            self.pipeline.set_state(gst.STATE_PLAYING)

    def is_playing(self):
        return gst.STATE_PLAYING in self.pipeline.get_state()

    def change_speed(self, delta):
        """Change the speed by DELTA

        :param delta: How to change current playback speed?
        """

        value = self.speed.get_property('speed') + delta
        self.speed.set_property('speed', value)
        print "Changed speed to %", value

    def get_file(self):
        return self.audiosrc.get_property('location')

    def __stop_seek(self):
        """Stop seeking, set back speed"""
        self.speed.set_property('speed', 1)
        self.volume.set_property('mute', False)

    def __reset_siddec(self):
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

    def __build_pipleine(self):
        """Internal helper to build the gstreamer pipleine"""

        self.pipeline = gst.Pipeline("sidplay-pipeline")

        self.audiosrc = gst.element_factory_make("filesrc", "audio")
        self.siddec = gst.element_factory_make('siddec', 'siddec')
        self.queue = gst.element_factory_make('queue', 'queue')
        self.speed = gst.element_factory_make('speed', 'speed')
        self.volume = gst.element_factory_make('volume', 'volume')
        self.sink = gst.element_factory_make("autoaudiosink", "sink")

        self.pipeline.add_many(self.audiosrc, self.siddec, self.queue, self.speed, self.volume, self.sink)
        gst.element_link_many(self.audiosrc, self.siddec, self.queue, self.speed, self.volume, self.sink)
