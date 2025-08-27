from openai import OpenAI
import sys
import os

client = OpenAI()

file_path = "output.txt"
if os.path.exists(file_path):
    os.remove(file_path)

input_filename = sys.argv[1]

audio_file= open(input_filename, "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file,
    response_format="text"
)
print(transcription)

file = open("output.txt", "w")
file.write(transcription)
file.close()