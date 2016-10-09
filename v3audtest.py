"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import threading

from math import log

import numpy as np
from numpy.fft import rfft

# open stream using callback (3)
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
wait_time = 10
 
audio = pyaudio.PyAudio()

buffer = 0

def process_input(maxf, maxp):
	print "blah"
 
wait_time = 2
MAX_FREQ = log(662 / 23, 2)
MIN_FREQ = log(23 / 23, 2)
threshold = 100

audio = pyaudio.PyAudio()

# define callback (2)
def configure_reader(config_path):
    with open(config_path) as fi:
        chars = fi.read().strip()

    print str(MAX_FREQ) + " " + str(MIN_FREQ)
    q_step = (MAX_FREQ - MIN_FREQ) / len(chars)
    print q_step
    def callback(in_data, frame_count, time_info, status):
        #print np.fromstring(in_data, dtype=np.int16)
        npdata = np.fromstring(in_data, dtype = np.int16)
        p = 20*np.log10(np.abs(rfft(npdata)))
        f = np.linspace(0, RATE/2.0, len(p))
        max_f = log((f[np.argmax(p)] + .1) / 23, 2)
        max_p = p[np.argmax(p)]
        if (max_f < MAX_FREQ and max_f >= MIN_FREQ and max_p > threshold):
            print str(max_f) + "  " + str(p[np.argmax(p)])
            char_ind =  int(max((MAX_FREQ - max_f) / q_step, 0.1))
            print char_ind
        return (in_data, pyaudio.paContinue)
    return callback

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK,
                stream_callback=configure_reader("conf.txt"))

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
#print "Waiting " + str(wait_time) + " seconds for input"
#time.sleep(wait_time)

raw_input("Press enter to quit...\n")

print 'Stopping stream...'
# stop stream (6)
#stream.stop_stream()
stream.close()
# close PyAudio (7)
audio.terminate()
print "Quitting now."
