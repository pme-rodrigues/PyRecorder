"""
    Insert a summary description of the file.
    ------
    TODO:
    -
"""

import soundcard as sc
import numpy as np
import wave
import threading


class PyRecorder:

    def __init__(self, device_name, filename="output.wav"):

        self.sample_rate = 48000
        self.block_size = 1024
        # SoundCard library processes audio data as floating-point numbers
        self.recorded_audio = np.empty((0, 2), dtype=np.float32)
        self.filename = filename
        self.rec_state = threading.Event()
        self.background_thread = None

        # Attempt to find the loopback device (used to record system audio)
        try:
            self.loopback_device = sc.get_microphone(
                device_name, include_loopback=True)
            print(f"Device with name '{device_name}' is ready to record")
        except ValueError:
            print(f"Loopback device with name '{device_name}' not found")

    def record(self):
        try:
            with self.loopback_device.recorder(samplerate=self.sample_rate, blocksize=self.block_size) as recorder:
                while not self.rec_state.is_set():
                    block = recorder.record(self.block_size)
                    self.recorded_audio = np.concatenate(
                        (self.recorded_audio, block), axis=0)

        except Exception as error_msg:
            print(error_msg)

    # Save the recording to a WAV file

    def save_wav(self):
        with wave.open(self.filename, 'wb') as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            # Convert the audio data to 16-bit integer format
            wav_data = (self.recorded_audio *
                        np.iinfo(np.int16).max).astype(np.int16)
            wav_file.writeframes(wav_data.tobytes())
        print(f'Wav file saved as {self.filename}.')


if __name__ == "__main__":

    device_name = input("Device name:\t")
    filename = "output.wav"
    rec = PyRecorder(device_name, filename)

    main_thread = None
    try:
        user_input = input('Enter (Yes) to start the recording:\t')
        if user_input.lower() == 'yes':
            print('Recording started. To stop the recording, enter (End) in the console.')
            # Start the main thread
            main_thread = threading.Thread(
                name='main program', target=rec.record)
            main_thread.start()

            while True:
                if input().lower() == 'end':
                    print('Terminating program')
                    rec.rec_state.set()
                    break
        else:
            raise ValueError(
                "Invalid input: Please enter 'yes' to start recording.")
    except ValueError as error_msg:
        print(error_msg)

    finally:
        if main_thread is not None:
            main_thread.join()
        rec.save_wav()
