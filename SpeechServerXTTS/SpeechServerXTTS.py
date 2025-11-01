from flask import Flask, request, send_file, jsonify
from TTS.api import TTS
import os
import tempfile

app = Flask(__name__)

# Carica il modello XTTS v2
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

@app.route('/tts', methods=['POST'])
def generate_tts():
    try:
        data = request.get_json()
        text = data.get("text", "") #prova a leggere la chiave "text" dal dizionario data; se "text" non esiste, restituisce il valore di default ""
        speaker = data.get("speaker", "Eugenio Mataracı")  #Se non è specificato un'altro Speaker di default usa Eugenio Mataracı

        print(f"--- Richiesta ricevuta ---")
        print(f"Testo: {text[:100]}")  # mostra i primi 100 caratteri
        print(f"Speaker: {speaker}")

        if not text:
            print("Errore: nessun testo fornito.")
            return jsonify({"error": "No text provided"}), 400

        # Salva l'audio temporaneo
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")  # crea un file temporaneo che tramite (delete=False) indica che non viene cancellato automaticamente
        print("Generazione TTS in corso...")

        tts.tts_to_file(
            text=text,
            speaker=speaker,
            language="en",
            file_path=tmp_wav.name
        )

        print(f"File generato: {tmp_wav.name}")
        return send_file(tmp_wav.name, mimetype="audio/wav")

    except Exception as e:
        import traceback
        print(" ERRORE XTTS:")
        traceback.print_exc()  #  mostra l'errore esatto
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5003)
