import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from piper.voice import PiperVoice
from pathlib import Path
from audio_generation import generate_audio, stream_audio

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        self.APP_TITLE = "Piper Read Aloud"
        self.setup_gui()
    
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

        self.text_entry = tk.Text(self.parent, height=20, width=50)
        self.text_entry.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.model_dropdown = ttk.Combobox(self.parent, width=10)
        self.model_dropdown.grid(row=1, column=0, sticky="NSEW")
        self.generate_btn = ttk.Button(self.parent, text="Generate", width=10, command=self.generate_audio)
        self.generate_btn.grid(row=1, column=1, sticky="NSEW")
        self.stream_btn = ttk.Button(self.parent, text="Stream", command=self.stream_audio)
        self.stream_btn.grid(row=2, column=0, sticky="NSEW")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)

    def open_file(self):
        filepath = filedialog.askopenfilename(parent=self.parent, filetypes=[("Text files", "*.txt")])
        if not filepath:
            return
        
        self.parent.title(f"{self.APP_TITLE} - {Path(filepath).name}")
        with open(filepath) as file:
            file_content = file.read()

        if self.text_entry.get("1.0", "end-1c"):
            answer = messagebox.askyesno("Do you want to proceed?", "Opening a new file will overwrite the curent text. Do you want to proceed?")
            if not answer:
                return
            
        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert("1.0", file_content)

    def save_file(self):
        filepath = filedialog.asksaveasfilename(parent=self.parent, filetypes=[("Text files", "*.txt")])
        if not filepath:
            return
        text_content = self.text_entry.get("1.0", "end-1c")
        try:
            with open(filepath, 'w') as file:
                file.write(text_content)
            if Path(filepath).exists():
                messagebox.showinfo("File saved successfully", f"File saved successfully at {filepath}")
                self.parent.title = f"{self.APP_TITLE} - {Path(filepath).name}"
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def confirm_save(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        if not text_content:
            return False
        answer = messagebox.askyesnocancel("Continue?", "This will close the current text. If you haven't saved it, loss of data could happen. \nDo you want to save the text file?")
        return answer


    def new_file(self):
        save_file = self.confirm_save()
        if save_file:
            self.save_file()
        elif save_file == None:
            return
        
        self.text_entry.delete("1.0", tk.END)
        self.parent.title = self.APP_TITLE
    
    def exit(self):
        save_file = self.confirm_save()
        if save_file:
            self.save_file()
        elif save_file == None:
            return
        self.parent.destroy()

    def generate_audio(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        if not text_content:
            messagebox.showwarning("Error", "Enter some text to generate audio")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave files", "*.wav")])
        generate_audio(text_content, self.model_dropdown.get(), filepath)
        if Path(filepath).exists():
            messagebox.showinfo("File saved successfully", f"File saved successfully at {filepath}")
        else:
            messagebox.showinfo("Error", "Error")

    def stream_audio(self):
        text_content = self.text_entry.get("1.0", "end-1c")
        if not text_content:
            messagebox.showwarning("Error", "Enter some text to generate audio")
            return
        stream_audio(text_content, self.model_dropdown.get())


if __name__ == "__main__":
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()