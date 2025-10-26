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
        // Avvia registrazione quando premi Z
        if (Input.GetKeyDown(pushToTalkKey))
            StartRecording();

        // Ferma registrazione quando rilasci Z
        if (Input.GetKeyUp(pushToTalkKey))
            StopRecordingAndSend();
    }

    private void StartRecording()
    {
        if (isRecording) return;

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

        string filePath = Path.Combine(Application.persistentDataPath, "user_recording.wav");
        SavWav.Save(filePath, recordedClip);

        string trascrizione = await SendAudioToWhisper(filePath);

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

    private async Task<string> SendAudioToWhisper(string filePath)
    {
        try
        {
            using (var client = new HttpClient())
            {
                var content = new MultipartFormDataContent();
                var fileBytes = File.ReadAllBytes(filePath);
                var fileContent = new ByteArrayContent(fileBytes);
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
                content.Add(fileContent, "file", "user_recording.wav");

                var response = await client.PostAsync(whisperUrl, content);
                string json = await response.Content.ReadAsStringAsync();

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
