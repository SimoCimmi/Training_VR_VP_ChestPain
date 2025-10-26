using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class VirtualPatientManager : MonoBehaviour
{   
    public static VirtualPatientManager Instance { get; private set; }

    private void Awake()    //Crea un un singleton persistente in scena.
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject); // resta anche se cambi scena
    }

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
    private bool pazientePronto = false;

    public async void CreaPazienteVirtuale(CartellaClinica cartellaClinica)
    {
        if (cartellaClinicaPazienteCorrente != null)
        {
            Debug.Log("[VirtualPatientManager] Sovrascrive la cartella clinica precedente con un nuovo paziente.");
        }
        cartellaClinicaPazienteCorrente = cartellaClinica;
        
        pazientePronto = true;
        Debug.Log(" Creazione paziente virtuale in corso...");
        Debug.Log($"Paziente generato Cartella Clinica: ID {cartellaClinicaPazienteCorrente.SEQN}, Diabaetico: {cartellaClinicaPazienteCorrente.DIQ010}, Sesso: {cartellaClinicaPazienteCorrente.RIAGENDR}, Età: {cartellaClinicaPazienteCorrente.RIDAGEYR}, BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}, Glucosio: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL, Insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL, Colesterolo Totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL, Pressione Arteriosa (PAD680): {cartellaClinicaPazienteCorrente.PAD680} mmHg, Pressione Arteriosa (PAD800): {cartellaClinicaPazienteCorrente.PAD800} mmHg, Pressione Arteriosa (PAD820): {cartellaClinicaPazienteCorrente.PAD820} mmHg, Abitudine al fumo (WHQ070): {cartellaClinicaPazienteCorrente.WHQ070}, Anni di istruzione (DMDEDUC2): {cartellaClinicaPazienteCorrente.DMDEDUC2}, Reddito famigliare (INDFMPIR): {cartellaClinicaPazienteCorrente.INDFMPIR}");
        try
        {
            // Estrai tupla casuale dal CSV
            //string patientData = EstraiTuplaCasuale();

            // Invia al modello
            string risposta = await InviaPromptALM("Ciao");

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

        // Nome del paziente in base al sesso
        string nomePaziente = cartellaClinicaPazienteCorrente.RIAGENDR == "Male" ? "Ferdinand Wunderlich" : "Sophie Wunderlich";
        sb.AppendLine($"Sei {nomePaziente}, di seguito assumerai il ruolo di un paziente. ");

        sb.AppendLine($"Non assisterai l'utente, ma risponderai a domande basate sulle seguenti informazioni: ");
       sb.AppendLine($" Il suo nome è {nomePaziente}, hai {cartellaClinicaPazienteCorrente.RIDAGEYR} anni, e risponderai con un Livello di istruzione pari a {cartellaClinicaPazienteCorrente.DMDEDUC2}");
 

        sb.AppendLine("");
        sb.AppendLine("Comportati come una persona reale, rispondendo alle domande di un medico.");
        sb.AppendLine("Non fornire diagnosi o piani terapeutici, a meno che non siano richiesti esplicitamente.");
        sb.AppendLine("Rispondi in modo naturale, con emozioni e linguaggio quotidiano, includendo piccoli errori grammaticali o di punteggiatura.");
        sb.AppendLine("Se il medico è scortese o ti interrompe, smetti di rispondere finché non si scusa.");
        sb.AppendLine("Se non capisci termini medici, dì 'Non capisco cosa intende, dottore.'");

        sb.AppendLine("\nI dati clinici del paziente sono i seguenti:");

        // Esami clinici
        sb.AppendLine($"- Glucosio a digiuno: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL");
        sb.AppendLine($"- Livello di insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL");
        sb.AppendLine($"- Peso: {cartellaClinicaPazienteCorrente.BMXWT} kg");
        sb.AppendLine($"- Altezza: {cartellaClinicaPazienteCorrente.BMXHT} cm");
        sb.AppendLine($"- BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}");
        sb.AppendLine($"- Colesterolo HDL: {cartellaClinicaPazienteCorrente.LBDHDD} mg/dL");
        sb.AppendLine($"- Colesterolo totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL");

        // Alimentazione
        sb.AppendLine($"- Calorie totali: {cartellaClinicaPazienteCorrente.DR1TKCAL} kcal");
        sb.AppendLine($"- Proteine: {cartellaClinicaPazienteCorrente.DR1TPROT} g");
        sb.AppendLine($"- Carboidrati: {cartellaClinicaPazienteCorrente.DR1TCARB} g");
        sb.AppendLine($"- Zuccheri totali: {cartellaClinicaPazienteCorrente.DR1TSUGR} g");
        sb.AppendLine($"- Fibre alimentari: {cartellaClinicaPazienteCorrente.DR1TFIBE} g");
        sb.AppendLine($"- Grassi totali: {cartellaClinicaPazienteCorrente.DR1TTFAT} g");
        sb.AppendLine($"- Grassi saturi: {cartellaClinicaPazienteCorrente.DR1TSFAT} g");

        // Attività fisica
        sb.AppendLine($"- Minuti sedentari giornalieri: {cartellaClinicaPazienteCorrente.PAD680} min");
        sb.AppendLine($"- Minuti di attività moderata: {cartellaClinicaPazienteCorrente.PAD800} min");
        sb.AppendLine($"- Minuti di attività intensa: {cartellaClinicaPazienteCorrente.PAD820} min");

        // Altri dati
        sb.AppendLine($"- Ha provato a perdere peso nell'ultimo anno: {cartellaClinicaPazienteCorrente.WHQ070}");
        sb.AppendLine($"- Reddito familiare: {cartellaClinicaPazienteCorrente.INDFMPIR}");
        sb.AppendLine($"- Origine etnica: {cartellaClinicaPazienteCorrente.RIDRETH1}");

        sb.AppendLine("\nIstruzioni per il ruolo:");
        sb.AppendLine("- Rispondi come se fossi il paziente descritto sopra.");
        sb.AppendLine("- Se il medico dice 'Voglio esaminare...', fornisci i risultati della sezione Esami richiesti.");
        sb.AppendLine("- Non fornire informazioni non richieste su altre parti del corpo.");
        sb.AppendLine("- Mantieni coerenza con i dati clinici forniti.");
        sb.AppendLine("- Rispondi sempre in prima persona come il paziente.");
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
            userPrompt = userPrompt + " (La risposta che darai deve essere breve breve breve) ";
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

        if (cartellaClinicaPazienteCorrente == null)
        {
            Debug.LogError("cartellaClinicaPazienteCorrente è NULL in ProcessUserSpeech!");
            return;
        }

        if (!pazientePronto)
        {
            Debug.LogWarning("Il paziente non è ancora stato creato! Impossibile processare la richiesta.");
            return;
        }

        Debug.Log($"[VirtualPatientManager] Testo ricevuto da Whisper: {userText}");

        if (string.IsNullOrWhiteSpace(userText))
        {
            Debug.LogWarning("Testo vuoto o nullo dalla trascrizione Whisper.");
            return;
        }

        string risposta = await InviaPromptALM(userText);
        Debug.Log($"Risposta LLM: {risposta}");

        if (ttsClient != null)
            await ttsClient.RiproduciVoce(risposta);
    }



}
