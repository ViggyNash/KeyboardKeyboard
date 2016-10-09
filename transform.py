import numpy as np
import pyaudio
import wave
from numpy.io import wavfile

a = np.array([1,2,3])
print type(a)

audio = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNKSIZE)
