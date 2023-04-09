import os
import threading
import tkinter as tk
from tkinter import ttk

def setup_enviroment():
    os.system("C:\\Users\\jeand\\anaconda3\\Scripts\\activate.bat && call conda.bat activate whisper && conda init powershell && cd C:\\Users\\jeand\\My Drive\\University\\ai\\SpeechToText\\ && conda activate whisper && pip install -r requirements.txt")
    # root.withdraw() has to be here or closed here. Unable to just add it here. Trying to find a alternitave
    os.system("python mic.py --model tiny --english")

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