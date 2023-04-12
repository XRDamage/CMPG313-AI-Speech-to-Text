# just to test the gui side without running the transcription model.

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import os
import signal



def visualize_audio():
    data = stream.read(CHUNK_SIZE)
    samples = np.frombuffer(data, dtype=np.int16)
    samples = samples / 32768.0
    wave = np.sin(np.arange(CHUNK_SIZE) * (1 * np.pi * 1 / CHUNK_SIZE))
    modulated_wave = samples * wave
    filtered_wave = lfilter(b, a, modulated_wave)
    line.set_ydata(filtered_wave)
    # ax.fill_between(x, 0, filtered_wave, where=filtered_wave>=0, interpolate=True, color='blue', alpha=0.25)
    # ax.fill_between(x, 0, filtered_wave, where=filtered_wave<0, interpolate=True, color='red', alpha=0.25)
    fig.canvas.draw()
    plt.pause(0.001)
    if streaming.get():
        root.after(1, visualize_audio)


def start_streaming():
    global streaming
    streaming.set(True)
    visualize_audio()

def stop_streaming():
    global streaming
    streaming.set(False)
    os.kill(os.getpid(), signal.SIGINT)



CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

fig = plt.Figure(facecolor='#2f2f2f', figsize=(2, 2))

ax = fig.add_subplot(111)

x = np.arange(0, CHUNK_SIZE)
line, = ax.plot(x, np.zeros(CHUNK_SIZE), color='#aaaaaa')

ax.set_ylim(-1, 1)
ax.set_xlim(0, CHUNK_SIZE)
ax.axis('off')

nyq = 0.5 * RATE
cutoff = 500
order = 5
normal_cutoff = cutoff / nyq
b, a = butter(order, normal_cutoff, btype='low', analog=False)


root = tk.Tk()
root.title("Transcription App")
root.resizable(width=False, height=False)
root.geometry("600x265")
root.config(bg="#2f2f2f")

top_frame = ttk.Frame(root, width=600, height=10, padding=10, style="DarkFrame.TFrame").grid(row=0, columnspan=2)
middle_frame = ttk.Frame(root, width=600, height=190, padding=10, style="LightFrame.TFrame").grid(row=1, columnspan=2)
bottom_frame = ttk.Frame(root, width=600, height=10, padding=10, style="DarkFrame.TFrame").grid(row=2, columnspan=2)

myOutput = tk.Text(master=middle_frame, wrap="word", height=12, width=50, background="#2f2f2f", bd=0, border=1)
myOutput.grid(row=1, column=1, columnspan=2)
canvas = FigureCanvasTkAgg(fig, master=middle_frame)
canvas.get_tk_widget().grid(row=1) 

streaming = tk.BooleanVar()
streaming.set(False)

buttonStart = ttk.Button(master=bottom_frame, text='Start', width=10, command=start_streaming, style="RoundButton.TButton")
buttonStart.grid(row=2, column=0)
buttonStop = ttk.Button(master=bottom_frame, text='Stop', width=10, style="RoundButton.TButton", command=stop_streaming)
buttonStop.grid(row=2, column=1)

style = ttk.Style()
style.configure("DarkFrame.TFrame", background="#2f2f2f")
style.configure("LightFrame.TFrame", background="#2f2f2f")
style.configure("RoundButton.TButton", foreground="black", background="#2f2f2f", borderwidth=0, focuscolor="#red", font=("Arial", 12), padding=10, relief="flat", borderradius=20)

root.mainloop()

stream.stop_stream()
stream.close()
p.terminate()
