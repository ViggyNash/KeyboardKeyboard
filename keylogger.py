#! /usr/bin/env python3

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
from time import sleep, time
import threading
import ctypes as ct
from ctypes.util import find_library
from math import sin, pi

import pyaudio

# linux only!
assert("linux" in sys.platform)


MIN_FREQ = 23
MAX_FREQ = 662
RATE = 44100
CHUNK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

# this will hold the keyboard state.  32 bytes, with each
# bit representing the state for a single key.
keyboard = (ct.c_char * 32)()

# these are the locations (byte, byte value) of special
# keys to watch
shift_keys = ((6,4), (7,64))
modifiers = {
    "left shift": (6,4),
    "right shift": (7,64),
    "left ctrl": (4,32),
    "right ctrl": (13,2),
    "left alt": (8,1),
    "right alt": (13,16)
}
last_pressed = set()
last_pressed_adjusted = set()
last_modifier_state = {}
caps_lock_state = 0

# key is byte number, value is a dictionary whose
# keys are values for that byte, and values are the
# keys corresponding to those byte values
key_mapping = {
    1: {
        0b00000010: "<esc>",
        0b00000100: ("1", "!"),
        0b00001000: ("2", "@"),
        0b00010000: ("3", "#"),
        0b00100000: ("4", "$"),
        0b01000000: ("5", "%"),
        0b10000000: ("6", "^"),
    },
    2: {
        0b00000001: ("7", "&"),
        0b00000010: ("8", "*"),
        0b00000100: ("9", "("),
        0b00001000: ("0", ")"),
        0b00010000: ("-", "_"),
        0b00100000: ("=", "+"),
        0b01000000: "<backspace>",
        0b10000000: "<tab>",
    },
    3: {
        0b00000001: ("q", "Q"),
        0b00000010: ("w", "W"),
        0b00000100: ("e", "E"),
        0b00001000: ("r", "R"),
        0b00010000: ("t", "T"),
        0b00100000: ("y", "Y"),
        0b01000000: ("u", "U"),
        0b10000000: ("i", "I"),
    },
    4: {
        0b00000001: ("o", "O"),
        0b00000010: ("p", "P"),
        0b00000100: ("[", "{"),
        0b00001000: ("]", "}"),
        0b00010000: "<enter>",
        #0b00100000: "<left ctrl>",
        0b01000000: ("a", "A"),
        0b10000000: ("s", "S"),
    },
    5: {
        0b00000001: ("d", "D"),
        0b00000010: ("f", "F"),
        0b00000100: ("g", "G"),
        0b00001000: ("h", "H"),
        0b00010000: ("j", "J"),
        0b00100000: ("k", "K"),
        0b01000000: ("l", "L"),
        0b10000000: (";", ":"),
    },
    6: {
        0b00000001: ("'", "\""),
        0b00000010: ("`", "~"),
        #0b00000100: "<left shift>",
        0b00001000: ("\\", "|"),
        0b00010000: ("z", "Z"),
        0b00100000: ("x", "X"),
        0b01000000: ("c", "C"),
        0b10000000: ("v", "V"),
    },
    7: {
        0b00000001: ("b", "B"),
        0b00000010: ("n", "N"),
        0b00000100: ("m", "M"),
        0b00001000: (",", "<"),
        0b00010000: (".", ">"),
        0b00100000: ("/", "?"),
        #0b01000000: "<right shift>",
    },
    8: {
        #0b00000001: "<left alt>",
        0b00000010: " ",
        0b00000100: "<caps lock>",
    },
    13: {
        #0b00000010: "<right ctrl>",
        #0b00010000: "<right alt>",
    },
}




def fetch_keys_raw(x11, display):
    x11.XQueryKeymap(display, keyboard)
    return keyboard



def fetch_keys(x11, display):
    global caps_lock_state, last_pressed, last_pressed_adjusted, last_modifier_state
    keypresses_raw = fetch_keys_raw(x11, display)


    # check modifier states (ctrl, alt, shift keys)
    modifier_state = {}
    for mod in modifiers:
        i, byte = modifiers[mod]
        modifier_state[mod] = bool(ord(keypresses_raw[i]) & byte)
    
    # shift pressed?
    shift = 0
    for i, byte in shift_keys:
        if ord(keypresses_raw[i]) & byte:
            shift = 1
            break

    # caps lock state
    if ord(keypresses_raw[8]) & 4: caps_lock_state = int(not caps_lock_state)


    # aggregate the pressed keys
    pressed = []
    for i, k in enumerate(keypresses_raw):
        o = ord(k)
        if o and i in key_mapping:
            for byte in key_mapping[i]:
                key = key_mapping[i][byte]
                if byte & o:
                    if isinstance(key, tuple): key = key[shift or caps_lock_state]
                    pressed.append(key)

    
    tmp = pressed
    pressed = list(set(pressed).difference(last_pressed))
    state_changed = tmp != last_pressed and (pressed or last_pressed_adjusted)
    last_pressed = tmp
    last_pressed_adjusted = pressed

    if pressed: pressed = pressed[0]
    else: pressed = None


    state_changed = last_modifier_state and (state_changed or modifier_state != last_modifier_state)
    last_modifier_state = modifier_state

    return state_changed, modifier_state, pressed


def log(done, callback, x11, display, sleep_interval=.005):
    while not done():
        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys(x11, display)
        if changed: callback(time(), modifiers, keys)

def make_callbacks(conf_path):
    with open(conf_path) as fil:
        chars = fil.read().strip()

    char_q = []
    q_step = (MAX_FREQ - MIN_FREQ) / len(chars)

    def key_callback(t, modifiers, keys):
        if keys != None and keys in chars or keys == '`':
            char_q.append(keys)

    def wrap_audio(aud):    
        def aud_callback(in_data, frame_count, time_info, status):
            if len(char_q) == 0:
                return (''.join(chr(128) for i in xrange(frame_count)), pyaudio.paContinue)
            elif char_q[len(char_q) - 1] == '`':
                aud.terminate()
                return (''.join(chr(128) for i in xrange(frame_count)), pyaudio.paComplete)
            print "After if"
            idx = chars.find(char_q[0])
            wave = ''
    def aud_callback(in_data, frame_count, time_info, status):
        print "cbk"
        if len(char_q) == 0:
            print "l 0"
            return (''.join(chr(128) for i in xrange(frame_count)), pyaudio.paContinue)
        elif char_q[len(char_q) - 1] == '`':
            print "term"
            close_cbk()
            return (''.join(chr(128) for i in xrange(frame_count)), pyaudio.paComplete)

        print "elif passed"

        idx = chars.find(char_q[0])
        wave = ''

        char_q.pop(0)
        if idx < 0:
            return (''.join(chr(128) for i in xrange(frame_count)), pyaudio.paContinue)

        freq = q_step * (len(chars) - idx)
        print "tone gen: " + freq

        for x in xrange(frame_count):
            wave = wave + chr(int(sin(x/((RATE/freq) / pi)) * 127 + 128))
        print "rwave"
        return (wave, pyaudio.paContinue)

    def keys_pred():
        return len(char_q) > 0 and char_q[len(char_q) - 1] == '`'

    return key_callback, keys_pred, aud_callback


if __name__ == "__main__":
    x11 = ct.cdll.LoadLibrary(find_library("X11"))
    display = x11.XOpenDisplay(None)

    key_han, key_pred, aud_han = make_callbacks("conf.txt")

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, output=True,
                frames_per_buffer=CHUNK,
                stream_callback=aud_han)

    stream.start_stream()

    thr = threading.Thread(target = log, args = (key_pred, key_han, x11, display))
    thr.setDaemon(True)
    thr.start()

    while stream.is_active():
        sleep(0.01)

    stream.close()
    audio.terminate()
    thr.join()
