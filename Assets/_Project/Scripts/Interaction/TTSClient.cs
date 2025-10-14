using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class TTSClient : MonoBehaviour
{
    // URL del server XTTS locale
    [SerializeField] private string ttsUrl = "http://127.0.0.1:5003/tts";
   
    [SerializeField] private AudioSource audioSource;  // AudioSource di Unity che riprodurrà l'audio generato

    private static readonly HttpClient client = new HttpClient
    {
        Timeout = TimeSpan.FromSeconds(100)
    };   // HttpClient statico per riutilizzare la connessione e non aprire più socket

    public async Task RiproduciVoce(string testo)   // Metodo principale per inviare testo a XTTS e riprodurre l'audio risultante
    {
        if (string.IsNullOrWhiteSpace(testo))   // Controlla se il testo è vuoto o contiene solo spazi
        {
            Debug.LogWarning("Testo vuoto, impossibile generare TTS.");
            return;
        }

        try
        {
            // Costruzione del JSON da inviare al server XTTS
            var json = "{\"text\":\"" + testo + "\",\"speaker\":\"Eugenio Mataracı\"}";
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await client.PostAsync(ttsUrl, content); // Invio della richiesta POST al server XTTS

            if (!response.IsSuccessStatusCode)
            {
                Debug.LogError($"Errore TTS server: {response.StatusCode}");
                return;
            }

            // Legge i byte dell'audio WAV restituito dal server
            var audioData = await response.Content.ReadAsByteArrayAsync();
            PlayAudioFromBytes(audioData);
        }
        catch (Exception ex)
        {
            Debug.LogError("Errore durante la richiesta a XTTS: " + ex.Message);
        }
    }

    // Converte i byte ricevuti in un AudioClip e lo riproduce tramite AudioSource
    private void PlayAudioFromBytes(byte[] wavData)
    {   
        // Crea un'istanza dell'helper WAV per leggere i dati audio
        WAV wav = new WAV(wavData);

        // Crea un AudioClip vuoto con il numero di campioni e frequenza del WAV
        AudioClip audioClip = AudioClip.Create("TTS_Audio", wav.SampleCount, 1, wav.Frequency, false);

        // Imposta i dati audio nel canale sinistro dell'AudioClip
        audioClip.SetData(wav.LeftChannel, 0);

        // Assegna il clip all'AudioSource e lo riproduce
        audioSource.clip = audioClip;
        audioSource.Play();
    }

     // Helper class per leggere un file WAV da un array di byte
    public class WAV
    {
         public float[] LeftChannel; // Dati del canale sinistro convertiti in float
        public int ChannelCount;    // Numero di canali audio
        public int SampleCount;     // Numero totale di campioni
        public int Frequency;       // Frequenza di campionamento (Hz)

        // Costruttore che legge i byte WAV
        public WAV(byte[] wav)
        {
            // Legge il numero di canali (offset 22 nel file WAV)
            ChannelCount = BitConverter.ToInt16(wav, 22);

            // Legge la frequenza di campionamento (offset 24)
            Frequency = BitConverter.ToInt32(wav, 24);

            // Trova la posizione della sezione 'data' nel file WAV
            int pos = 12;
            while (!(wav[pos] == 100 && wav[pos + 1] == 97 && wav[pos + 2] == 116 && wav[pos + 3] == 97)) pos += 4;
            pos += 8;

            // Calcola il numero di campioni effettivi
            SampleCount = (wav.Length - pos) / 2 / ChannelCount;

            // Inizializza l'array dei dati del canale sinistro
            LeftChannel = new float[SampleCount];

            int i = 0;
            // Converte ogni campione in float (-1.0 .. 1.0)
            while (pos < wav.Length)
            {
                LeftChannel[i] = BytesToFloat(wav[pos], wav[pos + 1]);
                pos += 2 * ChannelCount; // Salta gli altri canali se stereo
                i++;
            }
        }

        // Converte due byte in un float normalizzato per Unity
        private static float BytesToFloat(byte first, byte second)
        {
            short s = (short)((second << 8) | first);
            return s / 32768.0f; // Normalizza da short [-32768,32767] a float [-1,1]
        }
    }
}
