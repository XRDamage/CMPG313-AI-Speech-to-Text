import streamlit as st;
import websockets;
import asyncio;
import base64; 
import json;
import pyaudio;
import os;

from pathlib import Path;

# Session State
if 'text' not in st.session_state:
        st.session_state['text'] = 'Listening..';
        st.session_state['run'] = False;

#print(st.session_state); - view changes to the session state

#Audio parameters
st.sidebar.header('Audio parameters');

FRAMES_PER_BUFFER = int(st.sidebar.text_input('Frames per buffer',3200));
FORMAT = pyaudio.paInt16;
CHANNELS = 1;
RATE = int(st.sidebar.text_input('Rate',16000)); 
p = pyaudio.PyAudio();

# open an audio stream with above parameter settings
stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    frames_per_buffer = FRAMES_PER_BUFFER
)

print(stream);

# Start or stop audio transcription
def start_listening():
    st.session_state['run'] = True;

def download_transcription():
    read_txt = open(download_transcription)
