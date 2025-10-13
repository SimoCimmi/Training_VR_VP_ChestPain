import os
import requests

# Costruisci percorso assoluto rispetto allo script
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(current_dir, "audio_test.wav")

url = "http://127.0.0.1:5004/stt"
files = {"file": open(audio_path, "rb")}

response = requests.post(url, files=files)
print(response.json())
