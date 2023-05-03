import soundcard as sc
import numpy as np
import wave
import threading


class PyRecorder:
    def __init__(self, device_name):
        self.sample_rate = 48000
        self.block_size = 1024

        # SoundCard library processes audio data as floating-point numbers
        self.recorded_audio = np.empty((0, 2), dtype=np.float32)
        self.rec_state = threading.Event()
        self.err_recording = False
        self.background_thread = None

        # Attempt to find the loopback device (used to record system audio)
        self.set_device(device_name)

    def record(self):
        try:
            with self.loopback_device.recorder(
                samplerate=self.sample_rate, blocksize=self.block_size
            ) as recorder:
                while not self.rec_state.is_set():
                    block = recorder.record(self.block_size)
                    self.recorded_audio = np.concatenate(
                        (self.recorded_audio, block), axis=0
                    )

        except Exception as error_msg:
            print(error_msg)
            self.err_recording = True

    def start_recording(self):
        if self.rec_state.is_set():
            self.rec_state.clear()
        self.background_thread = threading.Thread(target=self.record)
        self.background_thread.start()

    def stop_recording(self):
        self.rec_state.set()
        self.background_thread.join()
        self.background_thread = None

    def set_filename(self, filename):
        self.filename = filename

    def reset_recording(self):
        self.recorded_audio = np.empty((0, 2), dtype=np.float32)

    def set_device(self, device_name):
        try:
            self.loopback_device = sc.get_microphone(device_name, include_loopback=True)
            print(f"Device with name '{device_name}' is ready to record")
        except ValueError:
            print(f"Loopback device with name '{device_name}' not found")

    def save_wav(self):
        with wave.open(self.filename, "wb") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_data = (self.recorded_audio * np.iinfo(np.int16).max).astype(
                np.int16
            )  # Convert the audio data to 16-bit integer format
            wav_file.writeframes(wav_data.tobytes())
        print(f"Wav file saved as {self.filename}.")
