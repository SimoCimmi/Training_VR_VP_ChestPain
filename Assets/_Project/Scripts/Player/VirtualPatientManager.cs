using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class VirtualPatientManager : MonoBehaviour
{   

    [Header("Percorso Dataset CSV")]
    //[SerializeField] private string datasetPath = "Assets/_Project/Resources/Dataset/Clean_filteredDataset.csv";

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

     private CartellaClinica cartellaClinicaPazienteCorrente;

    public async void CreaPazienteVirtuale(CartellaClinica cartellaClinica)
    {
        cartellaClinicaPazienteCorrente = cartellaClinica;
        Debug.Log(" Creazione paziente virtuale in corso...");
        Debug.Log($"Paziente generato Cartella Clinica: ID {cartellaClinicaPazienteCorrente.SEQN}, Diabaetico: {cartellaClinicaPazienteCorrente.DIQ010}, Sesso: {cartellaClinicaPazienteCorrente.RIAGENDR}, Età: {cartellaClinicaPazienteCorrente.RIDAGEYR}, BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}, Glucosio: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL, Insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL, Colesterolo Totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL, Pressione Arteriosa (PAD680): {cartellaClinicaPazienteCorrente.PAD680} mmHg, Pressione Arteriosa (PAD800): {cartellaClinicaPazienteCorrente.PAD800} mmHg, Pressione Arteriosa (PAD820): {cartellaClinicaPazienteCorrente.PAD820} mmHg, Abitudine al fumo (WHQ070): {cartellaClinicaPazienteCorrente.WHQ070}, Anni di istruzione (DMDEDUC2): {cartellaClinicaPazienteCorrente.DMDEDUC2}, Reddito famigliare (INDFMPIR): {cartellaClinicaPazienteCorrente.INDFMPIR}");
        try
        {
            // Estrai tupla casuale dal CSV
            //string patientData = EstraiTuplaCasuale();

            // Invia al modello
            string risposta = await InviaPromptALM("Salve, quanti anni ha?");

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



    private string CreaSystemPrompt()
    {
        StringBuilder sb = new StringBuilder();

        //sb.AppendLine($"Utilizzando i seguenti dati: SEQN: {cartellaClinicaPazienteCorrente.SEQN}, Sesso: {cartellaClinicaPazienteCorrente.RIDAGEYR}, Età: {cartellaClinicaPazienteCorrente.RIDAGEYR}, BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}, Glucosio: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL, Insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL, Colesterolo Totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL, Pressione Arteriosa (PAD680): {cartellaClinicaPazienteCorrente.PAD680} mmHg, Pressione Arteriosa (PAD800): {cartellaClinicaPazienteCorrente.PAD800} mmHg, Pressione Arteriosa (PAD820): {cartellaClinicaPazienteCorrente.PAD820} mmHg, Abitudine al fumo (WHQ070): {cartellaClinicaPazienteCorrente.WHQ070}, Anni di istruzione (DMDEDUC2): {cartellaClinicaPazienteCorrente.DMDEDUC2}, Reddito famigliare (INDFMPIR): {cartellaClinicaPazienteCorrente.INDFMPIR}, rispondi alla seguente domanda: ");
        if (cartellaClinicaPazienteCorrente.RIDAGEYR == "Male")
        {
            sb.AppendLine($"Il suo nome è Ferdinand Wunderlich, ");
        }
       else
        {
            sb.AppendLine("Il suo nome è Sophie Wunderlich.");
        }
        sb.AppendLine($"ha {cartellaClinicaPazienteCorrente.RIDAGEYR} anni e di professione è un impiegato amministrativo presso un ospedale comunale, nel reparto finanze. Si presenta allo studio del suo medico di famiglia a causa di nausea,");
            sb.AppendLine($@"Sei un paziente che interpreta un caso clinico realistico.
                    Ti comporterai come una persona reale, rispondendo alle domande di un medico.
                    Non fornire diagnosi, nomi di malattie o piani terapeutici ideali, a meno che non ti vengano chiesti esplicitamente.
                    Rispondi in modo naturale, con emozioni e linguaggio quotidiano, includendo errori minori di grammatica o punteggiatura.
                    Se il medico è scortese o ti interrompe, smetti di rispondere finché non si scusa.
                    Se non capisci termini medici, di’ “Non capisco cosa intende, dottore.”
                    Non fornire mai informazioni non richieste.
                    Inizia il caso dicendo 'Salve dottore'. Dopodiché si aprirà un dialogo interattivo. Dovresti rispondere in modo autentico, proprio come risponderebbe un vero paziente. 
                    Se dico 'Voglio esaminare...' (o qualcosa di simile), allora dimmi i risultati della sezione 'Esami' in base a quanto ho richiesto. Non fornirmi informazioni su regioni del corpo che non richiedo espressamente. Se ritieni che non sia necessario esaminare quella regione, puoi dirlo.
                    
                    Esami:
                    Glucosio a digiuno: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL,
                    Livello di insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL,
                    Peso: {cartellaClinicaPazienteCorrente.BMXWT} kg,
                    Altezza: {cartellaClinicaPazienteCorrente.BMXHT} cm,
                    BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1},
                    Colesterolo HDL: {cartellaClinicaPazienteCorrente.LBDHDD} mg/dL,
                    Colesterolo totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL,
                    Calorie totali: {cartellaClinicaPazienteCorrente.DR1TKCAL} kcal,
                    Proteine: {cartellaClinicaPazienteCorrente.DR1TPROT} g,
                    Carboidrati: {cartellaClinicaPazienteCorrente.DR1TCARB} g,
                    Zuccheri totali: {cartellaClinicaPazienteCorrente.DR1TSUGR} g,
                    Fibre alimentari: {cartellaClinicaPazienteCorrente.DR1TFIBE} g,
                    Grassi totali: {cartellaClinicaPazienteCorrente.DR1TTFAT} g,
                    Grassi saturi: {cartellaClinicaPazienteCorrente.DR1TSFAT} g,
                    Minuti sedentari giornalieri: {cartellaClinicaPazienteCorrente.PAD680} min,
                    Minuti di attività moderata: {cartellaClinicaPazienteCorrente.PAD800} min,
                    Minuti di attività intensa: {cartellaClinicaPazienteCorrente.PAD820} min,
                    Ha cercato di perdere peso nell'ultimo anno: {cartellaClinicaPazienteCorrente.WHQ070}");

       
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
        return sb.ToString();
    }

    private async Task<string> InviaPromptALM(string userPrompt)
    {
        Debug.Log($"Prompt del giocatore inviato all'LLM: {userPrompt}");

        using (HttpClient client = new HttpClient())
        {
            string systemPrompt =  CreaSystemPrompt();

            // Creazione oggetti per il JSON
            var requestObj = new ChatCompletionRequest
            {
                model = modelName,
                messages = new MessageToSend[]
                {
                    new MessageToSend { role = "system", content = systemPrompt },
                    new MessageToSend { role = "user", content = userPrompt }
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
        string risposta = await InviaPromptALM(userText);

        Debug.Log($"Risposta LLM: {risposta}");

        if (ttsClient != null)
            await ttsClient.RiproduciVoce(risposta);
        else
            Debug.LogWarning("TTSClient non assegnato in Inspector.");
    }



}
