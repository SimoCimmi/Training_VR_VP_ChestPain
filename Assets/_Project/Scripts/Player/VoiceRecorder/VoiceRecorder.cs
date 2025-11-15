using UnityEngine;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

public class VoiceRecorder : MonoBehaviour
{
    [Header("Server Whisper")]
    [SerializeField] private string whisperUrl = "http://127.0.0.1:5004/stt";

    [Header("Push-To-Talk Setting")]
    [SerializeField] private KeyCode pushToTalkKey = KeyCode.Z; // adesso usa il tasto Z

    private AudioClip recordedClip;
    private bool isRecording = false;

    void Update()
    {
        if (VirtualPatientManager.Instance == null)
        {
            Debug.Log("Paziente non ancora creato!");
            return;
        }

        // Avvia registrazione solo se paziente pronto e turno giocatore
        if (Input.GetKeyDown(pushToTalkKey))
        {
            if (VirtualPatientManager.Instance.IsPatientSpawned && VirtualPatientManager.Instance.IsPlayerTurn)
                StartRecording();
            else
                Debug.Log("Impossibile registrare: paziente non pronto o non è il tuo turno.");
        }

        // Ferma registrazione sempre se stavi registrando
        if (Input.GetKeyUp(pushToTalkKey) && isRecording)
        {
            StopRecordingAndSend();
        }
    }


    private void StartRecording()
    {
        if (isRecording) return;
        if (!VirtualPatientManager.Instance.IsPlayerTurn)
        {
            Debug.Log("Non puoi registrare, non è il tuo turno!");  //Se non compare controlla in console che non sia selezionata la spunta su Collapse il quale raggruppa tutti i log identici in un unico entry nella Console.
            return;
        }

        recordedClip = Microphone.Start(null, false, 10, 44100);
        isRecording = true;
        Debug.Log("🎙️ Registrazione iniziata...");
    }

    private async void StopRecordingAndSend()
    {
        if (!isRecording) return;

        Microphone.End(null);
        isRecording = false;
        Debug.Log("🎙️ Registrazione terminata, invio a Whisper...");

        if (recordedClip == null)
        {
            Debug.LogError("Registrazione audio non valida. Nessun clip registrato.");
            return;
        }

        if(VirtualPatientManager.Instance != null)
        {
            VirtualPatientManager.Instance.OnGiocatoreFinitoDiParlare();
        }

        string filePath = Path.Combine(Application.persistentDataPath, "user_recording.wav");
        SavWav.Save(filePath, recordedClip);

        string trascrizione = await SendAudioToSTT(filePath);

        if (VirtualPatientManager.Instance != null && !string.IsNullOrWhiteSpace(trascrizione))
        {
            Debug.Log("Chiama ProcessUserSpeech passandogli il testo sintetizzato");
            VirtualPatientManager.Instance.ProcessUserSpeech(trascrizione);
        }
        else
        {
            Debug.LogWarning("Problema: VirtualPatientManager.Instance nullo o trascrizione vuota.");
        }
    }

    private async Task<string> SendAudioToSTT(string filePath)
    {
        try
        {
            using (var client = new HttpClient())   //Crea un oggetto HttpClient (all’interno di un blocco using per essere automaticamente eliminato dopo l’uso).
            {
                var content = new MultipartFormDataContent();   //Crea un contenitore multipart/form-data, necessario per inviare file
                var fileBytes = File.ReadAllBytes(filePath);    //Legge tutto il contenuto del file audio e lo carica in memoria come array di byte.
                var fileContent = new ByteArrayContent(fileBytes);  //Converte i byte del file in un oggetto HttpContent, che può essere aggiunto al corpo della richiesta HTTP.
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav"); //Imposta il tipo MIME del file, in questo caso audio/wav, per indicare al server che tipo di file sta ricevendo.
                content.Add(fileContent, "file", "user_recording.wav"); //Aggiunge il file al contenuto multipart, assegnandogli il nome del campo "file" e un nome file fittizio "user_recording.wav".

                var response = await client.PostAsync(whisperUrl, content); //Invia la richiesta POST asincrona all’indirizzo whisperUrl
                string json = await response.Content.ReadAsStringAsync();   //Legge la risposta del server come stringa (presumibilmente in formato JSON).

                Debug.Log("Risposta Whisper grezza: " + json);

                int start = json.IndexOf(":") + 2;
                int end = json.LastIndexOf("\"");
                string testoPulito = json.Substring(start, end - start);

                Debug.Log("Risposta Whisper con testo pulito: " + testoPulito);
                return testoPulito;
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Errore nell'invio audio a Whisper: " + ex.Message);
            return null;
        }
    }
}
