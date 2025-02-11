from pyrecorder import PyRecorder
import soundcard as sc
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import re


class PyRecorderGUI(tk.Frame):
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.pack()
        self.configure(bg="#242424")
        self.create_widgets()
        self.rec = PyRecorder()

        # Ensure proper behaviour when unexpected window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_closing)

    def create_widgets(self):
        # Select Device button
        self.select_device_button = tk.Button(
            self,
            text="Select Device",
            font=("Arial", 10, "bold"),
            bg="#a41c1c",
            fg="#f2f2f2",
            width=13,
            height=1,
            relief="flat",
            command=self.select_device,
        )
        self.select_device_button.grid(row=0, column=0, padx=10, pady=10)

        # Start and Stop buttons
        self.start_button = tk.Button(
            self,
            text="Start \u25B6",
            font=("Arial", 10, "bold"),
            bg="#a41c1c",
            fg="#f2f2f2",
            width=13,
            height=1,
            relief="flat",
            command=self.start_recording_event,
        )

        # Record duration label
        self.duration_label = tk.Label(
            self, bg="#242424", fg="#f2f2f2", font=("Arial", 14)
        )

        # Device name label
        self.device_label = tk.Label(
            self, bg="#242424", fg="#f2f2f2", font=("Arial", 8)
        )

    def select_device(self):
        self.device_selection_window = tk.Toplevel(self.root)
        self.device_selection_window.title("Select Device")
        self.device_selection_window.geometry("300x250")
        self.device_selection_window.configure(bg="#242424")
        self.device_selection_window.grab_set()

        self.device_listbox = tk.Listbox(self.device_selection_window)
        self.device_listbox.grid(row=0, padx=10, pady=10, sticky="EW")

        self.microphones = sc.all_microphones(include_loopback=True)
        for mic in self.microphones:
            self.device_listbox.insert(tk.END, mic.name)

        self.confirm_button = tk.Button(
            self.device_selection_window,
            text="Confirm",
            font=("Arial", 10, "bold"),
            bg="#a41c1c",
            fg="#f2f2f2",
            relief="flat",
            command=self.device_selected,
        )
        self.confirm_button.grid(row=1, padx=10, pady=10, sticky="N")
        self.device_selection_window.columnconfigure(0, weight=1)

    def device_selected(self):
        selected_index = self.device_listbox.curselection()
        if selected_index:
            selected_device = self.microphones[selected_index[0]]
            self.rec.loopback_device = selected_device
            self.show_start_button()
            self.update_device_label()
            self.select_device_button.grid(row=0, column=0, padx=10, pady=10)
            self.device_selection_window.destroy()
        else:
            messagebox.showwarning(
                "Warning", "No device selected. Please select a device."
            )

    def update_device_label(self):
        self.device_label.config(text=f"Device: {self.rec.loopback_device}")
        self.device_label.grid(row=0, column=1, padx=10, pady=2, sticky="W")

    def show_start_button(self):
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

    def start_recording_event(self):
        self.rec.start_recording()
        self.select_device_button.config(state="disabled")
        self.start_button.config(text="Stop \u25A0", command=self.stop_recording_event)
        self.duration_label.config(text="00:00:00")
        self.duration_label.grid(row=1, column=1, padx=10, pady=10, sticky="W")
        self.update_duration_label()

    def update_duration_label(self):
        if self.rec.is_recording:
            duration = self.rec.duration
            self.duration_label.config(text=duration)
            # Update the label every 500 ms
            self.after(500, self.update_duration_label)

    def on_window_closing(self):
        if self.rec.is_recording:
            self.rec.stop_recording()
        self.rec.reset_recording()
        self.root.destroy()

    def stop_recording_event(self):
        self.rec.stop_recording()

        while True:
            filename = simpledialog.askstring(
                "Save Recording", "Enter filename:", parent=self.root
            )

            if filename is None:  # Cancel
                break

            is_valid, warning_message = self._validate_filename(filename)

            if not is_valid:
                if warning_message is not None:
                    self._show_warning("Invalid Filename", warning_message)
                continue

            self.rec.filename = filename
            self.rec.save_wav()
            break

        self.rec.reset_recording()
        self.start_button.config(
            text="Start \u25B6", command=self.start_recording_event
        )

        self.select_device_button.config(state="normal")

    def _validate_filename(self, filename):
        if len(filename) < 1:
            return False, "Filename cannot be empty. Please try again."
        pattern = r"^[A-Za-z][A-Za-z0-9]*$"
        if not re.match(pattern, filename):
            return (
                False,
                "The filename must start with a letter and contain only letters and numbers. Please try again.",
            )

        return True, None

    def _show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("PyRecorder")
    root.minsize(300, 50)
    root.configure(bg="#242424")
    root.pack_propagate(True)
    app = PyRecorderGUI(root=root)
    app.mainloop()
