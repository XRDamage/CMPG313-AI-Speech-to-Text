import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import queue
import tempfile
import os
import threading
import click
import torch
import numpy as np
import tkinter as tk
from tkinter import ttk
import pyaudio
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

@click.command()
@click.option("--model", default="base", help="Model to use", type=click.Choice(["tiny","base", "small","medium","large"]))
@click.option("--english", default=False, help="Whether to use English model",is_flag=True, type=bool)
@click.option("--verbose", default=False, help="Whether to print verbose output", is_flag=True,type=bool)
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option("--dynamic_energy", default=False,is_flag=True, help="Flag to enable dynamic engergy", type=bool)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option("--save_file",default=False, help="Flag to save file", is_flag=True,type=bool)
def main(model, english,verbose, energy, pause,dynamic_energy,save_file):
    temp_dir = tempfile.mkdtemp() if save_file else None

    #there are no english models for large
    if model != "large" and english:
        model = model + ".en"

    # whisper modal is called here:
    audio_model = whisper.load_model(model)
    audio_queue = queue.Queue()
    result_queue = queue.Queue()

    # calling record_audio and transcribe_forever in separate threads.    
    threading.Thread(target=record_audio,
                     args=(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir)).start()
    threading.Thread(target=transcribe_forever,
                     args=(audio_queue, result_queue, audio_model, english, verbose, save_file)).start()
    
    # displayibg output to textbox as live transcription takes place
    while True:
        myOutput.insert('end', result_queue.get() + '\n')
        myOutput.yview_moveto(1)
    
    


def record_audio(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir):
    #load the speech recognizer and set the initial energy threshold and pause threshold
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        #get and save audio as a temp wav file
        print("Say something!")
        i = 0
        while True:
            audio = r.listen(source)
            if save_file:
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                filename = os.path.join(temp_dir, f"temp{i}.wav")
                audio_clip.export(filename, format="wav")
                audio_data = filename
            else:
                torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                audio_data = torch_audio

            audio_queue.put_nowait(audio_data)
            i += 1


def transcribe_forever(audio_queue, result_queue, audio_model, english, verbose, save_file):
    while True:
        audio_data = audio_queue.get()
        if english:
            result = audio_model.transcribe(audio_data,language='english')
        else:
            result = audio_model.transcribe(audio_data)

        if not verbose:
            predicted_text = result["text"]
            result_queue.put_nowait("You said: " + predicted_text + "\n")
        else:
            result_queue.put_nowait(result)

        if save_file:
            os.remove(audio_data)



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
    threading.Thread(target=main).start()
    global streaming
    streaming.set(True)
    visualize_audio()

def stop_streaming():
    global streaming
    streaming.set(False)


root = tk.Tk()
root.title("Transcription App")
root.resizable(width=False, height=False)
root.geometry("600x265")
root.config(bg="#2f2f2f")

top_frame = ttk.Frame(root, width=600, height=10, padding=10, style="DarkFrame.TFrame").grid(row=0, columnspan=2)
middle_frame = ttk.Frame(root, width=600, height=190, padding=10, style="LightFrame.TFrame").grid(row=1, columnspan=2)
bottom_frame = ttk.Frame(root, width=600, height=10, padding=10, style="DarkFrame.TFrame").grid(row=2, columnspan=2)

myOutput = tk.Text(master=middle_frame, wrap="word", height=12, width=50, background="#2f2f2f", foreground="white", border=1)
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
