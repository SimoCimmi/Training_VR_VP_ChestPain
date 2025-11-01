# test_xtts.py
import torch
import os

# --- Workaround safe globals (solo se hai installato coqui-tts/TTS) ---
try:
    # importa la classe di config e la aggiunge ai safe globals di torch
    from TTS.tts.configs.xtts_config import XttsConfig
    torch.serialization.add_safe_globals([XttsConfig])
    print("Added XttsConfig to torch safe globals")
except Exception as e:
    print("Safe-globals workaround non applicato (continuo comunque):", e)

# --- import API TTS dopo il workaround ---
from TTS.api import TTS

# scegli GPU se disponibile
use_gpu = torch.cuda.is_available()
print("GPU disponibile:", use_gpu)

# carica il modello (scarica automaticamente se non presente)
model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(model_name, gpu=use_gpu)

# testi di prova
#text_it = "Mi dispiace, non capisco!"
#text_en = "Hello, I am a virtual patient for medical training. I am a 45-year-old male experiencing mild fatigue and occasional headaches. My blood pressure is slightly elevated, and I sometimes feel anxious during check-ups. I prefer to speak in English and answer questions clearly. Please ask me about my recent medical history, lifestyle, and any current symptoms, so we can practice accurate diagnosis and patient communication."
text_en = "Hello, I am a virtual patient for medical training."

#out_it = "xtts_output_it.wav"
out_en = "xtts_output_en.wav"
'''
print("Generazione (italiano)...")
tts.tts_to_file(
    text=text_it,
    file_path=out_it,
    speaker="Eugenio Mataracı",   # speaker predefinito
    language="it"
)
'''

print("Generazione (english)...")
tts.tts_to_file(
    text=text_en,
    file_path=out_en,
    speaker="Craig Gutsy",# - Andrew Chipper - Royston Min
    language="en"
)


# riproduce con simpleaudio (se installato)
try:
    import simpleaudio as sa
    for p in (out_en):
        if os.path.exists(p):
            print("Riproduco", p)
            wave_obj = sa.WaveObject.from_wave_file(p)
            play_obj = wave_obj.play()
            play_obj.wait_done()
except Exception as e:
    print("Riproduzione automatica non disponibile:", e)

print("FINITO. File:", out_en)
