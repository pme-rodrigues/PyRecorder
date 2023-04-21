from pyrecorder import PyRecorder
import soundcard as sc
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


class PyRecorderGUI(tk.Frame):
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.select_device_button = tk.Button(
            self, text="Select Device", command=self.select_device
        )
        self.select_device_button.grid(row=0, column=0, padx=10, pady=10)

        self.quit_button = tk.Button(self, text="Quit", command=self.root.destroy)
        self.quit_button.grid(row=0, column=1, padx=10, pady=10)

    def select_device(self):
        self.device_selection_window = tk.Toplevel(self.root)
        self.device_selection_window.title("Select Device")
        self.device_selection_window.geometry("300x250")
        self.device_selection_window.grab_set()

        self.device_listbox = tk.Listbox(self.device_selection_window)
        self.device_listbox.grid(row=0, padx=10, pady=10, sticky="EW")

        self.microphones = sc.all_microphones(include_loopback=True)
        for mic in self.microphones:
            self.device_listbox.insert(tk.END, mic.name)

        self.confirm_button = tk.Button(
            self.device_selection_window, text="Confirm", command=self.device_selected
        )
        self.confirm_button.grid(row=1, padx=10, pady=10, sticky="N")

        self.device_selection_window.columnconfigure(0, weight=1)

    def device_selected(self):
        selected_index = self.device_listbox.curselection()
        if selected_index:
            selected_device = self.microphones[selected_index[0]]
            self.rec = PyRecorder(selected_device.name)
            self.device_selection_window.destroy()
            self.show_start_button()
        else:
            messagebox.showwarning(
                "Warning", "No device selected. Please select a device."
            )

    def show_start_button(self):
        self.start_button = tk.Button(
            self, text="Start Recording", command=self.start_recording
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        self.select_device_button.destroy()

    def start_recording(self):
        self.rec.start_recording()
        self.start_button.config(text="Stop Recording", command=self.stop_recording)

    def stop_recording(self):
        self.rec.stop_recording()

        filename = simpledialog.askstring(
            "Save Recording", "Enter filename:", parent=self.root
        )
        if filename:
            self.rec.set_filename(filename)
            self.rec.save_wav()
            self.rec.reset_recording()

        self.start_button.config(text="Start Recording", command=self.start_recording)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("PyRecorder")
    root.geometry("300x50")
    app = PyRecorderGUI(root=root)
    app.mainloop()
