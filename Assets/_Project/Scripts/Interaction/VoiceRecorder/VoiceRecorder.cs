using UnityEngine;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

public class VoiceRecorder : MonoBehaviour
{
    [Header("Server Whisper")]
    [SerializeField] private string whisperUrl = "http://127.0.0.1:5004/stt";

    [Header("Riferimento al VirtualPatientManager")]
    [SerializeField] private VirtualPatientManager virtualPatientManager;

    private AudioClip recordedClip;
    private bool isRecording = false;

    public void OnMouseDown()  // clic sul microfono
    {
        if (!isRecording)
            StartRecording();
        else
            StopRecordingAndSend();
    }

    private void StartRecording()
    {
        recordedClip = Microphone.Start(null, false, 10, 44100);
        isRecording = true;
        Debug.Log("Registrazione iniziata...");
    }

    private async void StopRecordingAndSend()
    {
        Microphone.End(null);
        isRecording = false;
        Debug.Log("Registrazione terminata, invio a Whisper...");

        string filePath = Path.Combine(Application.persistentDataPath, "user_recording.wav");
        SavWav.Save(filePath, recordedClip);

        string trascrizione = await SendAudioToWhisper(filePath);

        if (virtualPatientManager != null && !string.IsNullOrWhiteSpace(trascrizione))
            virtualPatientManager.ProcessUserSpeech(trascrizione);
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

                // Il server Whisper restituisce {"text": "..."}
                int start = json.IndexOf(":") + 2;
                int end = json.LastIndexOf("\"");
                string testoPulito = json.Substring(start, end - start);

                return testoPulito; 
                Debug.Log("Risposta Whisper con testo pulito: " + json);
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Errore nell'invio audio a Whisper: " + ex.Message);
            return null;
        }
    }
}
