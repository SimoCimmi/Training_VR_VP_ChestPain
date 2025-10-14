using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class VirtualPatientManager : MonoBehaviour
{
    [Header("Percorso Dataset CSV")]
    [SerializeField] private string datasetPath = "Assets/_Project/Resources/Dataset/Clean_filteredDataset.csv";

    [Header("LM Studio API")]
    [SerializeField] private string lmStudioUrl = "http://127.0.0.1:1234/v1/chat/completions";  //completions (Completamento delle chat): Invia una cronologia delle chat al modello per prevedere la prossima risposta dell'assistente
    [SerializeField] private string modelName = "meta-llama-3-8b-instruct";

    [Header("TTS")]
    [SerializeField] private TTSClient ttsClient;

    [Serializable]
    private class MessageToSend
    {
        public string role;
        public string content;
    }

    [Serializable]
    private class ChatCompletionRequest
    {
        public string model;
        public MessageToSend[] messages;
    }

    public async void CreaPazienteVirtuale()
    {
        Debug.Log(" Creazione paziente virtuale in corso...");

        try
        {
            // Estrai tupla casuale dal CSV
            string patientData = EstraiTuplaCasuale();

            // Crea prompt completo
            string fullPrompt = CreaPromptCompleto(patientData);

            // Invia al modello
            string risposta = await InviaPromptALM(fullPrompt);

            Debug.Log($" LLM Studio: {risposta}");

            // Se hai assegnato il TTSClient via Inspector
            if (ttsClient != null)
            {
                await ttsClient.RiproduciVoce(risposta);
            }
            else
            {
                Debug.LogWarning("TTSClient non assegnato nell'Inspector. Assegna AudioManager -> TTSClient.");
            }


            //PAssa la risposat a XTTS per la sintesi vocale
            //.3FindObjectOfType<TTSClient>().RiproduciVoce(risposta);
            
        }
        catch (Exception ex)
        {
            Debug.LogError(" Errore durante la creazione del paziente virtuale: " + ex.Message);
        }
    }

    private string EstraiTuplaCasuale()
    {
        if (!File.Exists(datasetPath))
            throw new FileNotFoundException($"File non trovato: {datasetPath}");

        var lines = File.ReadAllLines(datasetPath);
        if (lines.Length < 2)
            throw new Exception("Dataset vuoto o invalido.");

        var random = new System.Random();
        string[] headers = lines[0].Split(',');
        string[] values = lines[random.Next(1, lines.Length)].Split(',');

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < headers.Length; i++)
            sb.AppendLine($"{headers[i]}: {values[i]}");

        return sb.ToString();
    }

    private string CreaPromptCompleto(string patientData)
    {
        StringBuilder sb = new StringBuilder();
        /*
                sb.AppendLine("SYSTEM PROMPT:");
                sb.AppendLine("Sei un paziente virtuale all’interno di una simulazione medica.");
                sb.AppendLine("Il tuo compito è simulare un paziente realistico basato sui seguenti dati clinici.");
                sb.AppendLine("Rispondi come una persona reale, con coerenza e umanità.");
                sb.AppendLine();

                sb.AppendLine(" DATI CLINICI:");
                sb.AppendLine(patientData);
                sb.AppendLine();

                sb.AppendLine("ROLE-PLAY:");
                sb.AppendLine("Comportati come un paziente vero. Rispondi in prima persona come se fossi il paziente.");
                sb.AppendLine();

                sb.AppendLine("ILLNESS SCRIPT:");
                sb.AppendLine("- Interpreta i dati per rappresentare la tua condizione medica.");
                sb.AppendLine("- Descrivi sintomi, storia e percezione personale.");
                sb.AppendLine();

                sb.AppendLine("Alla fine di questo messaggio, rispondi con: \"Sono pronto a rispondere alle domande del medico.\"");
        */
        sb.AppendLine("Ciao, come stai? (Rispondi con una risposta molto breve)");
        return sb.ToString();
    }

    private async Task<string> InviaPromptALM(string prompt)
    {
        Debug.Log($"Prompt del giocatore inviato all'LLM: {prompt}");

        using (HttpClient client = new HttpClient())
        {
            string systemPrompt = "Devi simulare un paziente.";

            // Creazione oggetti per il JSON
            var requestObj = new ChatCompletionRequest
            {
                model = modelName,
                messages = new MessageToSend[]
                {
                    new MessageToSend { role = "system", content = systemPrompt },
                    new MessageToSend { role = "user", content = prompt }
                }
            };

            string json = JsonUtility.ToJson(requestObj);
            Debug.Log($"JSON inviato a LM Studio:\n{json}");

            var content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                var response = await client.PostAsync(lmStudioUrl, content);
                string result = await response.Content.ReadAsStringAsync();
                Debug.Log($"JSON ricevuto da LM Studio:\n{result}");

                var jsonObj = JsonUtility.FromJson<ChatCompletionResponse>(result);
                if (jsonObj?.choices != null && jsonObj.choices.Length > 0)
                    return jsonObj.choices[0].message.content;

                return "Nessuna risposta dal modello.";
            }
            catch (Exception ex)
            {
                Debug.LogError($"Errore durante la richiesta a LM Studio: {ex.Message}");
                return null;
            }
        }
    }

    // Classi per deserializzare il JSON della risposta
    [Serializable]
    private class ChatCompletionResponse
    {
        public Choice[] choices;
    }

    [Serializable]
    private class Choice
    {
        public Message message;
    }

    [Serializable]
    private class Message
    {
        public string role;
        public string content;
    }

    public async void ProcessUserSpeech(string userText)
    {
        Debug.Log($"[VirtualPatientManager] Testo ricevuto da Whisper: {userText}");

        if (string.IsNullOrWhiteSpace(userText))
        {
            Debug.LogWarning("Testo vuoto o nullo dalla trascrizione Whisper.");
            return;
        }

        // Invia il testo dell’utente all’LLM per generare una risposta
        string risposta = await InviaPromptALM(userText  +  " (Rispondi con una risposta molto breve ed in italiano)");

        Debug.Log($"Risposta LLM: {risposta}");

        if (ttsClient != null)
            await ttsClient.RiproduciVoce(risposta);
        else
            Debug.LogWarning("TTSClient non assegnato in Inspector.");
    }



}
