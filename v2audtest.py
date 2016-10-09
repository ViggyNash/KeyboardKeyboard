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
CHUNK = 1024
<<<<<<< HEAD
wait_time = 10
 
audio = pyaudio.PyAudio()

buffer = 0

def process_input(maxf, maxp):
	print "blah"
 
=======
wait_time = 2
MAX_FREQ = 662
MIN_FREQ = 20 

audio = pyaudio.PyAudio()

>>>>>>> 209104f6e1715c6897507e1409dd8be7b0d3c7a5
# define callback (2)
def configure_reader(config_path):
    with open(config_path) as fi:
        chars = fi.read()

    q_step = (MAX_FREQ - MIN_FREQ) / len(chars)
    def callback(in_data, frame_count, time_info, status):
        #print np.fromstring(in_data, dtype=np.int16)
        npdata = np.fromstring(in_data, dtype = np.int16)
        p = 20*np.log10(np.abs(rfft(npdata)))
        f = np.linspace(0, RATE/2.0, len(p))
        max_f = f[np.argmax(p)]
        if (max_f >= MIN_FREQ):
            print str(max_f) + "  " + str(p[np.argmax(p)])
            char_ind = max((MAX_FREQ - int(max_f) - MIN_FREQ) / q_step, 0)
            print chars[char_ind]
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
