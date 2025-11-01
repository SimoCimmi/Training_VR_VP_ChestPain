# 🩺 Training_VR_VP

Questo progetto è un fork di una piattaforma di simulazione medica basata su **Unity**, estesa per aumentare il livello di interattività attraverso l’integrazione di moduli di sintesi e riconoscimento vocale (**Whisper** e **XTTS v2**) e di un modello linguistico di grandi dimensioni (**LLM**) tramite LM-Studio.

Il sistema consente di simulare conversazioni medico–paziente realistiche, fornendo uno strumento avanzato per il training clinico e la formazione.

---
## ⚙️ Setup:

## A. 🎮 Unity

### 1. Installazione di Unity
-  Scarica e installa Unity Hub.
-  Apri il progetto in Unity utilizzando la **versione 6000.1.2f1** (se necessario installala).



### 2. Avvio della scena
-  Apri la scena: StudioMedico.unity che si trova in Training_VR_VP\Assets_Project\Scenes\
- Premi **Play** in Unity per lanciare la simulazione.

---

## B. 🎙️ Whisper Setup

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

1. Scarica da **[FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)** il file "ffmpeg-release-essentials.zip" che si trova nella sezione **release builds**

2. Estrai la cartella "ffmpeg-8.0-essentials_build" in:
    ```bash
    C:\Tirocinio_Utils
    ```

3. Aggiungi alle variabili d'ambiente nella sezione PATH il seguente percorso:
    ```bash
    C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin
    ```

4. Verifica l’installazione:

- Lanciando il comando
    ```bash
    where ffmpeg
    ```
    vedrai se correttamente installato, il seguente output:
    
    C:\Tirocinio_Utils\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe


- Lanciando il comando
    ```bash
    ffmpeg -version
    ```
    dira se è presente o meno ffmpeg

### 3. Esecuzione di Whisper

```bash
cd C:\Training_VR_VP\WhisperServer
whisper_env\Scripts\activate
python WhisperServer.py
```
Nota: Whisper funzionerà su CPU (più lento) se non è presente GPU compatibile.

### 4. Whisper (Opzionale) 
È possibile modificare il modello utilizzato scegliendo tra cinque versioni di Whisper:
tiny, base, small, medium e large — disposte in ordine crescente di accuratezza e tempo di elaborazione.
In altre parole, tiny è il modello più veloce ma meno preciso, mentre large è il più accurato, sebbene più lento.


---

## C. 🔈XTTS v2 – Setup

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
Lanciare i seguenti comandi sempre nell'ambiente virtuale di XTTS creato.
```bash
pip install coqui-tts
pip install simpleaudio
pip install flask
```
⚠️ Se ricevi l’errore:
```bash
error: Microsoft Visual C++ 14.0 or greater is required
```
Installa **[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/it/visual-cpp-build-tools/)** e seleziona “Sviluppo di applicazioni desktop con C++” durante l’installazione.

### 4. Esecuzione di XTTS
```bash
cd C:\Training_VR_VP\SpeechServerXTTS
xtts_env\Scripts\activate
python SpeechServerXTTS.py
```

### 5. Note su XTTS v2

- XTTS-v2 è utilizzato con licenza non commerciale per fini di ricerca ( **[Licenza ufficiale](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt)**)

- XTTS offre diversi modelli vocali chiamati Speaker, che sono i seguenti:
    ```bash
    cd C:\Training_VR_VP\SpeechServerXTTS
    xtts_env\Scripts\activate
    tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idx
    ```
  Di default sono stati utilizzati:
  - Daisy Studious (per l'Inglese femminile)
  - Craig Gutsy (per l'Inglese maschile)

  Ma se si preferisce interagire in italiano si cosiglia di cambiare gli Speaker nel file "Training_VR_VP\Assets\_Project\Scripts\Player\VirtualPatientManager.cs" con:
    - Ana Florence (per l'Italiano femminile)
    - Eugenio Mataracı (per l'italiano maschile)    
    
    E di modificare nel file "Training_VR_VP\SpeechServerXTTS\SpeechServerXTTS.py" il campo language da "en" ad "it" 

---

## D. 🧠 LM-Studio Setup

- Scarica e installa **[LM-Studio](https://lmstudio.ai/download)**.
- Scarica il modello desiderato.
- Avvia LM-Studio.
- Seleziona il modello e imposta Status: Running nella sezione Develop.
- Nota: Controllare che l'indirizzo tramite cui è raggiungibile LM-Studio sia lo stesso utilizzato nel progetto Unity (attualemnte è utilizzato "http://127.0.0.1:1234")

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