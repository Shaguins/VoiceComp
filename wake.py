import pvporcupine
import pyaudio
import struct
import whisper
import sounddevice as sd
import numpy as np
import wave
import os
import imageio_ffmpeg as ffmpeg
print(ffmpeg.get_ffmpeg_exe())

#takes access key from my key.txt file so that my key isn't public
with open("key.txt", "r") as file:
    accessKey = file.read().strip()
    
porcupine = pvporcupine.create(
        access_key=accessKey,
        keywords=["blueberry"]
    )

model = whisper.load_model("tiny")
    
def recordAudio(duration=5, filename="command.wav"):
    """Record audio for a few seconds after wake word"""
    fs = 16000
    print("Listening for your command...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    filepath = os.path.join(os.getcwd(), filename)
    wave_file = wave.open(filename, "wb")
    wave_file.setnchannels(1)
    wave_file.setsampwidth(2)
    wave_file.setframerate(fs)
    wave_file.writeframes(recording.tobytes())
    wave_file.close()
    return filepath

def waitingForWake ():

    
    audio = pyaudio.PyAudio()
    audio_stream = audio.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    print("listening")

    
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                #print(recordAudio())
                audioPath = recordAudio()
                try:
                    saying = model.transcribe(audioPath, fp16=False)
                except FileNotFoundError:
                    print("not working" + audioPath)
                    exit()
                command = saying["text"].strip()
                print("you said "+command)
                break

    except KeyboardInterrupt:
        print("stopping")
    finally:
        audio_stream.close()
        audio.terminate()
        porcupine.delete()
        
waitingForWake()