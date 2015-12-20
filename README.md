# Python SID playback
Simple library to play back SID tunes using Gstreamer and Python

# Dependencies
You will at least the following packes:

 * gstreamer0.10-plugins-ugly (for `siddec`)
 * gstreamer0.10-plugins-good (for `autoaudiosink`)
 * python-gst0.10 (Python gstreamer binding)
 * Python2 - There are bindings for Gstreamer and Python3, too - so porting all this to Python3 seems doable
 
# Usage
Run `python2 sidplay.py /path/to/sid/file` to start playback.

You can control speed with `+` and `-`. 
Next / previous song of current directory can be played typing `p` and `n`
`Space` for pause