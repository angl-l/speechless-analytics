"""Vosk is used to transcribe meetings

This records from the microphone, transcribes speech with Vosk, prints the
transcript, and saves it to transcript.csv.
"""

import json
import csv
import time
import queue
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer


MODEL_PATH = "model/vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000
OUTPUT_FILE = "transcript.csv"

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

print("Start speaking. Press Ctrl+C to stop.")

full_text = ""

# records start time of transcription per row
start= time.perf_counter()

try:
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            data = q.get()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("You said:", text)
                    full_text += text + " "

except KeyboardInterrupt:
    print("\nStopped recording.")


final_result = json.loads(recognizer.FinalResult())
final_text = final_result.get("text", "")

if final_text:
    print("Final:", final_text)
    full_text += final_text + " "

# records end time of transcription per row
end = time.perf_counter()

timestamp = datetime.now().isoformat()
words = full_text.split(" ")
name = words[0]
raw_text = " ". join(words[1:])
time_taken_sec = end - start

with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # if .csv empty, add header rows first and then add transcription
    if f.tell() == 0:
        writer.writerow(["timestamp", "name", "raw_script", "time_taken_sec"])

    writer.writerow([timestamp, name, raw_text, time_taken_sec])
    

print(f"\nSaved to {OUTPUT_FILE}")
print("Transcript:", full_text.strip())
