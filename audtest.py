import pyaudio
import wave
 
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
 
audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print "recording..."
frames = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print "finished recording"
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()


import scipy as sp
import scipy.signal as sci_sig
from scipy.fftpack import fft
import matplotlib.pyplot as plt

def bandpass_filt(lowcut, highcut, fs = RATE):
    low = lowcut
    high = highcut
    b, a = sci_sig.butter(5, [low, high], btype='bandpass', analog = True, output = 'ba')
    return b, a

def apply_filter(low, high, data, fs = RATE):
    b, a = bandpass_filt(low, high, fs)
    return sci_sig.lfilter(b, a, data)

import numpy as np
'''
numpydata = b''.join(frames)
numpydata = np.fromstring(numpydata, dtype = np.int16)
t = 20*np.log10(np.arange(numpydata.size)*1.0/RATE)
numpydata = np.abs(np.fft.rfft(numpydata))
#numpydata = apply_filter(0, 10000, numpydata)
f = np.linspace(0, RATE/2.0, numpydata.size)

plt.plot(f, numpydata)
plt.show()
'''

numpydata = np.array(frames)

#print numpydata
'''
p = 20*np.log10(np.abs(np.fft.rfft(numpydata[:1024, 0])))
f = np.linspace(0, RATE/2.0, len(p))
pl.plot(f, numpydata)
pl.xlabel("Frequency(Hz)")
pl.ylabel("Power(dB)")
pl.show()
''' 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()