# 🩺 Training_VR_VP - Setup & Execution Guide

Questo progetto unisce **Unity**, **Whisper** e **XTTS v2** per la gestione vocale e la simulazione in ambiente VR.

---

## ⚙️ Requisiti Generali

- **Sistema operativo:** Windows 10 o superiore  
- **Python:** Versione **3.10.10** (necessario per XTTS v2)  
- **Unity:** Versione **6000.1.2f1**  
- **FFmpeg:** installato e configurato nel PATH  
- **Connessione Internet** (per il download dei modelli Whisper e XTTS)

---

## 🎮 Unity Setup

### 1. Installazione di Unity
1. Scarica e installa Unity Hub.
2. All’apertura del progetto, assicurati di installare la **versione 6000.1.2f1**.
3. Una volta completata l’installazione, apri la scena: Training_VR_VP\Assets_Project\Scenes\StudioMedico.unity


### 2. Avvio della scena
Premi **Play** in Unity per lanciare la simulazione.

---

## 🗣️ Whisper Setup

### 1. Creazione dell’ambiente virtuale
Apri il **Prompt dei comandi (CMD)** ed esegui:

```bash
cd C:\Training_VR_VP\WhisperServer
python -m venv whisper_env
whisper_env\Scripts\activate
python -m pip install --upgrade pip
pip install git+https://github.com/openai/whisper.git
pip install torch
pip install flask
```

Se riscontri problemi di compatibilità con Torch:

```bash

pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
```

### 2.🗣️ FFmpeg Setup

1. Scarica da FFmpeg Builds (https://www.gyan.dev/ffmpeg/builds/) il file ffmpeg-release-essentials.zip che si trova nella sezione release builds

2. Estrai la cartella ffmpeg-8.0-essentials_build in:
```bash
C:\Tirocinio_Utils
```

3. Aggiungi a PATH come nuova variabile d’ambiente:
```bash
C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin
```

4. Verifica l’installazione:

Lanciando il comando
```bash
where ffmpeg
```
vedrai se correttamente installato, il seguente outpute:
C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe


Lanciando il comando
```bash
ffmpeg -version
```
dira se è presente o meno ffmpeg

5. Esecuzione di Whisper
```bash
cd C:\Training_VR_VP\WhisperServer
whisper_env\Scripts\activate
python WhisperServer.py
```
Whisper funzionerà su CPU (più lento) se non è presente GPU compatibile.
---
### 2.🗣️ XTTS v2 Setup
1. Installazione di Python 3.10.10

Scarica e installa Python 3.10.10
, assicurandoti di spuntare “Add to PATH” durante l’installazione.

Per impostarlo come versione di default:

py -0
echo [defaults]> "%LOCALAPPDATA%\py.ini"
echo python=3.10>> "%LOCALAPPDATA%\py.ini"
py -0

2. Creazione dell’ambiente virtuale
cd C:\Training_VR_VP\SpeechServerXTTS
python -m venv xtts_env
xtts_env\Scripts\activate
python -m pip install --upgrade pip

3. Installazione dei pacchetti

Installa PyTorch (seguendo le istruzioni su pytorch.org/get-started/locally
)
Poi installa:

pip install coqui-tts
pip install simpleaudio
pip install flask


⚠️ Se ricevi l’errore:
error: Microsoft Visual C++ 14.0 or greater is required
Installa i Microsoft C++ Build Tools

e seleziona “Sviluppo di applicazioni desktop con C++” durante l’installazione.

4. Esecuzione di XTTS
cd C:\Training_VR_VP\SpeechServerXTTS
xtts_env\Scripts\activate
python SpeechServerXTTS.py

5. Note su XTTS v2

XTTS-v2 è utilizzato con licenza non commerciale per fini di ricerca.
Licenza ufficiale

Per visualizzare i modelli vocali installati:

tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idx

🧠 LM-Studio Setup

Scarica e installa LM-Studio.

Scarica il modello desiderato.

Avvia LM-Studio.

Seleziona il modello e imposta Status: Running nella sezione Develop.

🚀 Avvio Completo del Sistema

Avvia LM-Studio e imposta il modello come attivo.

Esegui Whisper:

cd C:\Training_VR_VP\WhisperServer
whisper_env\Scripts\activate
python WhisperServer.py


Esegui XTTS:

cd C:\Training_VR_VP\SpeechServerXTTS
xtts_env\Scripts\activate
python SpeechServerXTTS.py


Avvia Unity e seleziona la scena:

Assets\_Project\Scenes\StudioMedico.unity


Premi Play per eseguire la simulazione VR completa.

📦 Autori & Crediti

Whisper: OpenAI Whisper

XTTS v2: Coqui TTS

LM-Studio: lmstudio.ai