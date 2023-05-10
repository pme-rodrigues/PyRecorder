import soundcard as sc
import numpy as np
import wave
import threading
import tempfile
import shutil
import os
import time


class PyRecorder:
    def __init__(self):
        self.sample_rate = None
        self.buffer_size = None
        self.block_size = 1024
        self.buffered_audio = []
        self.rec_state = threading.Event()
        self.background_thread = None
        self._loopback_device = None
        self._filename = ""
        self.temp_filename = ""
        self.t0 = 0

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def loopback_device(self):
        return self._loopback_device.name

    @loopback_device.setter
    def loopback_device(self, device):
        self._loopback_device = device

        # If loopback_device is mono, set sample_rate to 16 kHz, otherwise 44.1 kHz
        self.sample_rate = 16000 if device.channels == 1 else 44100

        # Set buffer size to record for about 3 seconds
        self.buffer_size = int(self.sample_rate * 3 / self.block_size)

        print(f"Device with name '{self._loopback_device.name}' is ready to record")

    @property
    def is_recording(self):
        return self.rec_state.is_set()

    @property
    def duration(self):
        elapsed_seconds = time.monotonic() - self.t0
        return time.strftime("%H:%M:%S", time.gmtime(elapsed_seconds))

    def record(self):
        # Create a temporary file to store the recorded audio data
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_filename = temp_file.name

        try:
            with self._loopback_device.recorder(
                samplerate=self.sample_rate, blocksize=self.block_size
            ) as recorder:
                with wave.open(self.temp_filename, "wb") as temp_wav_file:
                    # Set WAV file parameters
                    temp_wav_file.setnchannels(self._loopback_device.channels)
                    temp_wav_file.setsampwidth(2)
                    temp_wav_file.setframerate(self.sample_rate)

                    while self.rec_state.is_set():
                        block = recorder.record(self.block_size)
                        self.buffered_audio.append(block)

                        if len(self.buffered_audio) == self.buffer_size:
                            self._write_to_temp(temp_wav_file)
                    # Make sure all data is saved
                    self._write_to_temp(temp_wav_file)

        except Exception as error_msg:
            print(error_msg)
            self.err_recording = True

    def _write_to_temp(self, temp_file):
        buffered_audio_data = np.concatenate(self.buffered_audio, axis=0)
        # Convert the audio data to 16-bit integer format
        wav_data = (buffered_audio_data * np.iinfo(np.int16).max).astype(np.int16)
        # Write audio data to the temporary WAV file
        temp_file.writeframes(wav_data.tobytes())
        self.buffered_audio.clear()

    def start_recording(self):
        if not self.rec_state.is_set():
            self.rec_state.set()
        self.background_thread = threading.Thread(target=self.record)
        self.background_thread.start()
        self._start_time()

    def _start_time(self):
        self.t0 = time.monotonic()

    def stop_recording(self):
        self.rec_state.clear()
        self.background_thread.join()
        self.background_thread = None

    def reset_recording(self):
        self.buffered_audio.clear()
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def save_wav(self):
        output_filename = self._filename + ".wav"
        shutil.copyfile(self.temp_filename, output_filename)
        print(f"Wav file saved as {output_filename}.")
