import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pathlib import Path
from PiperReadAloudGUI.audio_generation import generate_audio, stream_audio, list_models, get_speaker_id_map
import threading


class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        self.APP_TITLE = "Piper Read Aloud"
        self.setup_gui()

    def _display_generate_label(func):
        def wrapper(self, *args, **kwargs):
            self.status_bar.set("Generating...")
            func(self, *args, **kwargs)
            self.status_bar.set("Done.")

        return wrapper

    def setup_gui(self):
        self.parent.title(self.APP_TITLE)
        self.menubar = tk.Menu(self.parent)
        self.parent.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="New file...", command=self.new_file)
        self.file_menu.add_command(label="Open file...", command=self.open_file)
        self.file_menu.add_command(label="Save file...", command=self.save_file)
        self.file_menu.add_command(label="Exit", command=self.exit)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.text_entry = tk.Text(self.parent, height=20, width=50, wrap=tk.WORD)
        self.text_entry.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.model_dropdown = ttk.Combobox(self.parent, state='readonly')
        self.model_dropdown.grid(row=1, column=0, sticky="NSEW")
        self.speaker_dropdown = ttk.Combobox(self.parent, state='readonly')
        self.speaker_dropdown.grid(row=1, column=1, sticky="NSEW")
        self.generate_btn = ttk.Button(
            self.parent,
            text="Generate",
            width=10,
            command=self.start_generate_audio_thread,
        )
        self.generate_btn.grid(row=2, column=1, sticky="NSEW")
        self.stream_btn = ttk.Button(
            self.parent, text="Stream", command=self.start_stream_audio_thread
        )
        self.stream_btn.grid(row=2, column=0, sticky="NSEW")
        self.status_bar = StatusBar(self.parent)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky='EW', pady=(5,0))
        self.build_dropdown()
        self.build_speakers_dropdown()
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)
        self.parent.protocol("WM_DELETE_WINDOW", self.exit)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.build_speakers_dropdown)

    def build_dropdown(self):
        available_models = list_models()
        self.model_dropdown["values"] = available_models or ["",]
        self.model_dropdown.current(0)
    
    def build_speakers_dropdown(self, event=None):
        model = self.model_dropdown.get()
        if not model:
            self.speaker_dropdown['values'] = ["",]
            return
        available_speakers = get_speaker_id_map(model)
        if available_speakers:
            self.speaker_dropdown['values'] = list(available_speakers)
        else:
            self.speaker_dropdown['values'] = ["Default"]
        self.speaker_dropdown.current(0)

    def open_file(self):
        filepath = filedialog.askopenfilename(
            parent=self.parent, filetypes=[("Text files", "*.txt")]
        )
        if not filepath:
            return

        self.parent.title(f"{self.APP_TITLE} - {Path(filepath).name}")
        with open(filepath) as file:
            file_content = file.read()

        if self.text_entry.get("1.0", "end-1c"):
            answer = messagebox.askyesno(
                "Do you want to proceed?",
                "Opening a new file will overwrite the curent text. Do you want to proceed?",
            )
            if not answer:
                return

        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert("1.0", file_content)

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            parent=self.parent, filetypes=[("Text files", "*.txt")]
        )
        if not filepath:
            return
        text_content = self.text_entry.get("1.0", "end-1c")
        self.status_bar.set("Saving...")
        try:
            with open(filepath, "w") as file:
                file.write(text_content)
            if Path(filepath).exists():
                messagebox.showinfo(
                    "File saved successfully", f"File saved successfully at {filepath}"
                )
                self.parent.title(f"{self.APP_TITLE} - {Path(filepath).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
        self.status_bar.set("Done.")

    def confirm_save(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        if not text_content:
            return False
        answer = messagebox.askyesnocancel(
            "Continue?",
            "This will close the current text. If you haven't saved it, loss of data could happen. \nDo you want to save the text file?",
        )
        return answer

    def new_file(self):
        save_file = self.confirm_save()
        if save_file:
            self.save_file()
        elif save_file == None:
            return

        self.text_entry.delete("1.0", tk.END)
        self.parent.title(self.APP_TITLE)

    def exit(self):
        save_file = self.confirm_save()
        if save_file:
            self.save_file()
        elif save_file == None:
            return
        self.parent.destroy()

    @_display_generate_label
    def generate_audio(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        speaker = self.speaker_dropdown.get() if self.speaker_dropdown.get() != "Default" else ""
        if not text_content:
            messagebox.showwarning("Error", "Enter some text to generate audio")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".wav", filetypes=[("Wave files", "*.wav")]
        )
        if not filepath:
            return
        self.generate_btn['state'] = 'disabled'
        generate_audio(text_content, self.model_dropdown.get(), filepath, speaker)
        self.generate_btn['state'] = 'normal'
        if Path(filepath).exists():
            messagebox.showinfo(
                "File saved successfully", f"File saved successfully at {filepath}"
            )
        else:
            messagebox.showinfo("Error", "Error")

    @_display_generate_label
    def stream_audio(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        speaker = self.speaker_dropdown.get() if self.speaker_dropdown.get() != "Default" else ""
        if not text_content:
            messagebox.showwarning("Error", "Enter some text to generate audio")
            return
        self.stream_btn['state'] = 'disabled'
        stream_audio(text_content, self.model_dropdown.get(), speaker)
        self.stream_btn['state'] = 'normal'

    def start_stream_audio_thread(self):
        thread = threading.Thread(target=self.stream_audio, daemon=True)
        thread.start()

    def start_generate_audio_thread(self):
        thread = threading.Thread(target=self.generate_audio, daemon=True)
        thread.start()

class StatusBar(tk.Frame):
    def __init__(self, parent, text=""):
        tk.Frame.__init__(self, parent)
        self.text = tk.StringVar()
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              textvariable=self.text)
        self.text.set(text or "Status Bar")
        self.label.pack(fill=tk.X)

    def set(self, text):
        self.text.set(text)

    def clear(self):
        self.text.set("")