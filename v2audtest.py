"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import threading

import numpy as np
from numpy.fft import rfft

# open stream using callback (3)
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 4096
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
wait_time = 2
 
audio = pyaudio.PyAudio()
 
# define callback (2)
def callback(in_data, frame_count, time_info, status):
    #print np.fromstring(in_data, dtype=np.int16)
    npdata = np.fromstring(in_data, dtype = np.int16)
    p = 20*np.log10(np.abs(rfft(npdata)))
    f = np.linspace(0, RATE/2.0, len(p))
    if (f[np.argmax(p)] >= 20):
    	print str(f[np.argmax(p)]) + "  " + str(p[np.argmax(p)])
    return (in_data, pyaudio.paContinue)

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
print "Waiting " + str(wait_time) + " seconds for input"
time.sleep(wait_time)
print 'Stopping stream...'
# stop stream (6)
#stream.stop_stream()
stream.close()
print 'Here!!'
# close PyAudio (7)
audio.terminate()
print "Quitting now."