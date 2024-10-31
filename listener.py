import wave
from dataclasses import dataclass, asdict
import pyaudio
import os
import glob
##this code is originally by musikalkemist and has been implemented into our program for educational purposes
##link to the original work https://github.com/musikalkemist/recorder
@dataclass
class StreamParams:
    format: int = pyaudio.paInt16
    channels: int = 1
    rate: int = 44100
    frames_per_buffer: int = 1024
    input: bool = True
    output: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class Recorder:
    """Recorder uses the blocking I/O facility from pyaudio to record sound
    from mic.

    Attributes:
        - stream_params: StreamParams object with values for pyaudio Stream
            object
    """
    def __init__(self, stream_params: StreamParams) -> None:
        self.stream_params = stream_params
        self._pyaudio = None
        self._stream = None
        self._wav_file = None

    def record(self, duration: int, save_path: str) -> None:
        """Record sound from mic for a given amount of seconds.

        :param duration: Number of seconds we want to record for
        :param save_path: Where to store recording
        """
        print("Start recording...")
        self._create_recording_resources(save_path)
        self._write_wav_file_reading_from_stream(duration)
        self._close_recording_resources()
        print("Stop recording")

    def _create_recording_resources(self, save_path: str) -> None:
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(**self.stream_params.to_dict())
        self._create_wav_file(save_path)

    def _create_wav_file(self, save_path: str):
        self._wav_file = wave.open(save_path, "wb")
        self._wav_file.setnchannels(self.stream_params.channels)
        self._wav_file.setsampwidth(self._pyaudio.get_sample_size(self.stream_params.format))
        self._wav_file.setframerate(self.stream_params.rate)

    def _write_wav_file_reading_from_stream(self, duration: int) -> None:
        for _ in range(int(self.stream_params.rate * duration / self.stream_params.frames_per_buffer)):
            audio_data = self._stream.read(self.stream_params.frames_per_buffer)
            self._wav_file.writeframes(audio_data)

    def _close_recording_resources(self) -> None:
        self._wav_file.close()
        self._stream.close()
        self._pyaudio.terminate()



from apis import run_apis_1
if __name__ == "__main__":
    cycles = 3
    secs = 3
    name = ""
    code = 0
    import time
    st = time.time()
    files = glob.glob('audio_stream/clips/*')
    if len(files)!=0:   
        for f in files:
            os.remove(f)


    for x in range (cycles):
        stream_params = StreamParams()
        recorder = Recorder(stream_params)
        recorder.record((secs + 1), f"audio_stream/clips/clip_{x}.wav")
        exa = f"audio_stream/clips/clip_{x}.wav"
        
        code, name, art, lang, lyric, ca = run_apis_1(exa)
        if lang == "Made up Language/gibberish": #made up
            print(name)
            print("Made up Langauge!!!")
            et = time.time()
            print(f"time = {et - st} seconds")
            break
        if code == 3: #perfect run
            print(name)
            print("NEW WAY FOUND!!!")
            et = time.time()
            print(f"time = {et - st} seconds")
            break
        if code == 2: #confirmed instrumental
            print(name)
            print("Confirmed Intrumental")
            et = time.time()
            print(f"time = {et - st} seconds")
            break
        if code == 1: #likely lyrics not recorded or is an instrumental
            print(name)
            print("Unlucky")
            et = time.time()
            print(f"time = {et - st} seconds")
            break
    if code == 0:
        print("Could retrieve nothing....")
        et = time.time()
        print(f"time = {et - st} seconds")


def run():
    cycles = 3
    secs = 3
    name = ""
    art = ""
    lang = ""
    lyric = ""
    ca = ""
    code = 0
    import time
    st = time.time()
    files = glob.glob('audio_stream/clips/*')
    if len(files) != 0:
        for f in files:
            os.remove(f)


    for x in range (cycles):
        stream_params = StreamParams()
        recorder = Recorder(stream_params)
        recorder.record((secs + 1), f"audio_stream/clips/clip_{x}.wav")
        exa = f"audio_stream/clips/clip_{x}.wav"
        
        code, name, art, lang, lyric, ca = run_apis_1(exa)
        if code == 4: #made up
            print(name)
            print("Made up Langauge!!!")
            et = time.time()
            print(f"time = {et - st} seconds")
            return code, name, art, lang, lyric, ca
        if code == 3: #perfect run
            print(name)
            print("NEW WAY FOUND!!!")
            et = time.time()
            print(f"time = {et - st} seconds")
            return code, name, art, lang, lyric, ca
            break
        if code == 2: #confirmed instrumental
            print(name)
            print("Confirmed Intrumental")
            et = time.time()
            print(f"time = {et - st} seconds")
            return code, name, art, lang, lyric, ca
        if code == 1: #likely lyrics not recorded or is an instrumental
            print(name)
            print("Unlucky")
            et = time.time()
            print(f"time = {et - st} seconds")
            return code, name, art, lang, lyric, ca
    if code == 0:
        print("Could retrieve nothing....")
        et = time.time()
        print(f"time = {et - st} seconds")
        return code, name, art, lang, lyric, ca