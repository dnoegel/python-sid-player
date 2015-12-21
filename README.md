# Python SID playback
Simple library to play back SID tunes using Gstreamer and Python

# Dependencies
You will at least the following packes:

 * gstreamer0.10-plugins-ugly (for `siddec`)
 * gstreamer0.10-plugins-good (for `autoaudiosink`)
 * python-gst0.10 (Python gstreamer binding)
 * Python2 - There are bindings for Gstreamer and Python3, too - so porting all this to Python3 seems doable
 
# Usage
This package provides two example usages.

## example_interactive.py

Run `python2 example_interactive.py /path/to/sid/file` to start playback.

 * You can control speed with `+` and `-`. 
 * Next / previous song of current directory can be played typing `p` and `n`
 * `Space` for pause
 * `s` in order to seek 10 seconds

## example_simple.py
Run `python2 example_simple.py /path/to/sid/file` to start playback.

It boils down to this snippet:

```
import gobject

from sidplay import SidBackend

app = SidBackend()
app.play(YOUR_FILE)

gobject.MainLoop().run()
```