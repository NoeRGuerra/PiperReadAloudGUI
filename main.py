import tkinter as tk
from tkinter import ttk
from piper.voice import PiperVoice

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        self.setup_gui()
    
    def setup_gui(self):
        self.parent.title("Piper Read Aloud")
        self.text_entry = tk.Text(self.parent, height=20, width=50)
        self.text_entry.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.model_dropdown = ttk.Combobox(self.parent, width=10)
        self.model_dropdown.grid(row=1, column=0, sticky="NSEW")
        self.generate_btn = ttk.Button(self.parent, text="Generate", width=10)
        self.generate_btn.grid(row=1, column=1, sticky="NSEW")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)

    def open_file(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()