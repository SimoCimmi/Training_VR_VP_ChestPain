from flask import Flask, request, jsonify
import whisper
import tempfile
import os

# Crea un'app Flask per gestire le richieste HTTP
app = Flask(__name__)

# Carica il modello Whisper (scegli tra "tiny", "base", "small", "medium", "large")
# Modelli più grandi = più precisi ma anche più lenti e pesanti
model = whisper.load_model("base")

@app.route('/stt', methods=['POST'])
def stt():
    try:
        # Verifica che la richiesta contenga un file chiamato 'file'
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        # Recupera il file audio inviato dal client
        audio_file = request.files['file']

        temp_path = os.path.join(os.getcwd(), "temp.wav")
        audio_file.save(temp_path)

        result = model.transcribe(temp_path, language='en')
        os.remove(temp_path)
        return jsonify({"text": result["text"]})

    except Exception as e:
        # Gestisce eventuali errori (es. formato audio non valido, errore nel modello, ecc.)
        return jsonify({"error": str(e)}), 500

# Avvia il server Flask sulla porta 5004 in locale
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004)
