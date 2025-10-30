# (IN AGGIORNAMENTO)

🩺 Training_VR_VP - Setup & Execution Guide

Questo progetto è un fork di una piattaforma di simulazione medica basata su **Unity**, estesa per aumentare il livello di interattività attraverso l’integrazione di moduli di sintesi e riconoscimento vocale (**Whisper** e **XTTS v2**) e di un modello linguistico di grandi dimensioni (**LLM**) tramite LM-Studio.

Il sistema consente di simulare conversazioni medico–paziente realistiche, fornendo uno strumento avanzato per il training clinico e la formazione professionale.

---
## ⚙️ Unity Setup

### 1. Installazione di Unity
-  Scarica e installa Unity Hub.
-  All’apertura del progetto, assicurati di installare la **versione 6000.1.2f1**.
-  Una volta completata l’installazione, apri la scena: Training_VR_VP\Assets_Project\Scenes\StudioMedico.unity


### 2. Avvio della scena
Premi **Play** in Unity per lanciare la simulazione.

---

## 🎙️ Whisper Setup

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

1. Scarica da **[FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)** il file ffmpeg-release-essentials.zip che si trova nella sezione release builds

2. Estrai la cartella ffmpeg-8.0-essentials_build in:
    ```bash
    C:\Tirocinio_Utils
    ```

3. Aggiungi alle variabili d'amnbiente nella sezione PATH il seguente percorso:
    ```bash
    C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin
    ```

4. Verifica l’installazione:

- Lanciando il comando
    ```bash
    where ffmpeg
    ```
    vedrai se correttamente installato, il seguente outpute:
    C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe


- Lanciando il comando
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
    Nota: Whisper funzionerà su CPU (più lento) se non è presente GPU compatibile.

---

## 🔈 2. XTTS v2 – Setup

### 1. Installazione di Python 3.10.10
Scarica e installa **[Python 3.10.10](https://www.python.org/downloads/windows/)**, 
assicurandoti di **spuntare “Add to PATH”** durante l’installazione.

Per impostarlo come versione di default:
```bash
py -0
echo [defaults]> "%LOCALAPPDATA%\py.ini"
echo python=3.10>> "%LOCALAPPDATA%\py.ini"
py -0
```


### 2. Creazione dell’ambiente virtuale
    ```bash
    cd C:\Training_VR_VP\SpeechServerXTTS
    python -m venv xtts_env
    xtts_env\Scripts\activate
    python -m pip install --upgrade pip
    ```

### 3. Installazione dei pacchetti

    Installa **[PyTorch](pytorch.org/get-started/locally/)** seguendo le istruzioni indicate.

### 4. Installa le seguenti librerie:

    ```bash
    pip install coqui-tts
    pip install simpleaudio
    pip install flask
    ```

⚠️ Se ricevi l’errore:
```bash
error: Microsoft Visual C++ 14.0 or greater is required
```
Installa i **[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/it/visual-cpp-build-tools/)** e seleziona “Sviluppo di applicazioni desktop con C++” durante l’installazione.

### 4. Esecuzione di XTTS
```bash
cd C:\Training_VR_VP\SpeechServerXTTS
xtts_env\Scripts\activate
python SpeechServerXTTS.py
```

### 5. Note su XTTS v2

- XTTS-v2 è utilizzato con licenza non commerciale per fini di ricerca. 
  **[Licenza ufficiale](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt)** 

- Per visualizzare i modelli vocali installati:
```bash
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idx
```

---

## 🧠 3. LM-Studio Setup

1. Scarica e installa LM-Studio.
2. Scarica il modello desiderato.
3. Avvia LM-Studio.
4. Seleziona il modello e imposta Status: Running nella sezione Develop.

---

## 🎮 Avvio Completo del Sistema

### 1. LM-Studio:
  - Avvia LM-Studio.
  - Seleziona il modello e imposta Status: Running nella sezione Develop.

### 2. Whisper:
```bash
cd C:\Training_VR_VP\WhisperServer
whisper_env\Scripts\activate
python WhisperServer.py
```

### 3. XTTS:
```bash
cd C:\Training_VR_VP\SpeechServerXTTS
xtts_env\Scripts\activate
python SpeechServerXTTS.py
```

### 4. Unity:
- Avvia Unity
- Seleziona la scena Training_VR_VP\Assets_Project\Scenes\StudioMedicounity
- Premi **Play** in Unity per lanciare la simulazione.

---

## 📦 Autori & Crediti

- Whisper: OpenAI Whisper
- XTTS v2: Coqui TTS
- LM-Studio: lmstudio.ai