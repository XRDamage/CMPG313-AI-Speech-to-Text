import os
import threading
import signal
import tkinter as tk
from tkinter import ttk

def setup_enviroment():
    # C:\\Users\\jeand\\anaconda3\\Scripts\\activate.bat && call conda.bat activate whisper && conda init powershell && cd C:\\Users\\jeand\\My Drive\\University\\ai\\SpeechToText\\ && conda activate whisper && pip install -r requirements.txt && python mic.py --model tiny --english
    os.system("C:\\Users\\jeand\\anaconda3\\Scripts\\activate.bat && call conda.bat activate whisper && conda init powershell && cd C:\\Users\\jeand\\My Drive\\University\\ai\\SpeechToText\\ && conda activate whisper")
    root.withdraw()
    os.system("python mic.py --model tiny --english")
    os.kill(os.getpid(), signal.SIGINT) # ensures whole program is terminated when it is closed.

# self explanatory, Plain GUI design
root = tk.Tk()

root.title("Loading Screen")
root.geometry("300x100")
root.eval('tk::PlaceWindow . center')
root.configure(bg="#333333")

label = tk.Label(root, text="Setting up environment", font=("Helvetica", 16), fg="white", bg="#333333")
label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
progress_bar.pack(pady=10)
progress_bar.start()

# call the setup in a separate thread to keep the main running.
threading.Thread(target=setup_enviroment).start()
# running main
root.mainloop()