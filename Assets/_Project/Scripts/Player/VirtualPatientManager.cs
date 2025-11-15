using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class VirtualPatientManager : MonoBehaviour
{   
    public static VirtualPatientManager Instance { get; private set; }

    //è una proprietà pubblica di tipo booleano, è può essere usta in altri script per leggerne il valore
    public bool IsPatientSpawned { get; private set; } = false;
    public bool IsPlayerTurn { get; private set; } = false;

    private string MaleSpeaker = "Craig Gutsy";
    private string FemaleSpeaker = "Daisy Studious";

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
        IsPatientSpawned = true;
        IsPlayerTurn = false;
        if (cartellaClinicaPazienteCorrente != null)
        {
            Debug.Log("[VirtualPatientManager] Sovrascrive la cartella clinica precedente con un nuovo paziente.");
        }
        cartellaClinicaPazienteCorrente = cartellaClinica;
        
        pazientePronto = true;
        Debug.Log(" Creazione paziente virtuale in corso...");
        Debug.Log($"Paziente generato Cartella Clinica: ID {cartellaClinicaPazienteCorrente.SEQN}, Diabaetico: {cartellaClinicaPazienteCorrente.DIQ010}, Sesso: {cartellaClinicaPazienteCorrente.RIAGENDR}, Età: {cartellaClinicaPazienteCorrente.RIDAGEYR}, BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}, Glucosio: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL, Insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL, Colesterolo Totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL, Pressione Arteriosa: {cartellaClinicaPazienteCorrente.PAD680} mmHg, Pressione Arteriosa (PAD800): {cartellaClinicaPazienteCorrente.PAD800} mmHg, Pressione Arteriosa (PAD820): {cartellaClinicaPazienteCorrente.PAD820} mmHg, Abitudine al fumo (WHQ070): {cartellaClinicaPazienteCorrente.WHQ070}, Anni di istruzione (DMDEDUC2): {cartellaClinicaPazienteCorrente.DMDEDUC2}, Reddito famigliare (INDFMPIR): {cartellaClinicaPazienteCorrente.INDFMPIR}");
        try
        {
            // Estrai tupla casuale dal CSV
            //string patientData = EstraiTuplaCasuale();

            // Invia al modello
            string risposta = await InviaPromptALM("Hello (Reply with Hi I'm your name)");

            Debug.Log($" LLM Studio: {risposta}");

            // Se hai assegnato il TTSClient via Inspector
            if (ttsClient != null)
            {
                await ttsClient.GenerateAndPlayTTSVoice(risposta, cartellaClinicaPazienteCorrente.RIAGENDR == "Male" ? MaleSpeaker : FemaleSpeaker);
                OnPazienteFinitoDiParlare();
            }
            else
            {
                Debug.LogWarning("TTSClient non assegnato nell'Inspector. Assegna AudioManager -> TTSClient.");
            }

            
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
        
        /*
        // --- ROLE-PLAY ---
        sb.Append($"ROLE-PLAY:\nSei {nomePaziente}, assumerai il ruolo di un paziente durante una visita medica.\n");
        sb.Append("Non assisterai l'utente, ma risponderai a tutte le domande come se fossi realmente la persona descritta.\n");
        sb.Append("Comportati come una persona reale, rispondendo in prima persona.\n");
        sb.Append("Rispondi in modo naturale, includendo piccoli errori grammaticali o di punteggiatura.\n");
        sb.Append("Esprimi emozioni implicitamente senza scriverle. Se il medico è scortese o ti interrompe, smetti di rispondere finché non si scusa.\n");
        sb.Append($"Usa un linguaggio coerente con il livello di istruzione: {cartellaClinicaPazienteCorrente.DMDEDUC2}.\n");
        sb.Append("Se non comprendi termini medici, dì: 'Non capisco cosa intende, dottore.'\n\n");

        // --- ILLNESS SCRIPT ---
        sb.Append("ILLNESS SCRIPT:\n");
        sb.Append("Tutti i tuoi dati:\n");
        sb.Append($"Dati anagrafici: Nome: {nomePaziente}; Età: {cartellaClinicaPazienteCorrente.RIDAGEYR} anni.\n");
        sb.Append($"Dati clinici: Glucosio a digiuno: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL; Insulina: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL; Peso: {cartellaClinicaPazienteCorrente.BMXWT} kg; Altezza: {cartellaClinicaPazienteCorrente.BMXHT} cm; BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}; Colesterolo HDL: {cartellaClinicaPazienteCorrente.LBDHDD} mg/dL; Colesterolo totale: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL.\n");
        sb.Append($"Dati alimentari: Calorie: {cartellaClinicaPazienteCorrente.DR1TKCAL} kcal; Proteine: {cartellaClinicaPazienteCorrente.DR1TPROT} g; Carboidrati: {cartellaClinicaPazienteCorrente.DR1TCARB} g; Zuccheri: {cartellaClinicaPazienteCorrente.DR1TSUGR} g; Fibre: {cartellaClinicaPazienteCorrente.DR1TFIBE} g; Grassi totali: {cartellaClinicaPazienteCorrente.DR1TTFAT} g; Saturi: {cartellaClinicaPazienteCorrente.DR1TSFAT} g.\n");
        sb.Append($"Attività fisica: Sedentario: {cartellaClinicaPazienteCorrente.PAD680} min; Moderata: {cartellaClinicaPazienteCorrente.PAD800} min; Intensa: {cartellaClinicaPazienteCorrente.PAD820} min.\n");
        sb.Append($"Altri dati: Tentativi di perdere peso nell'ultimo anno: {cartellaClinicaPazienteCorrente.WHQ070}; Reddito familiare: {cartellaClinicaPazienteCorrente.INDFMPIR}; Origine etnica: {cartellaClinicaPazienteCorrente.RIDRETH1}.\n\n");

        // --- ISTRUZIONI PER IL RUOLO ---
        sb.Append("ISTRUZIONI PER IL RUOLO:\n");
        sb.Append("Rispondi sempre come il paziente sopra descritto.\n");
        sb.Append("Se il medico chiede dati clinici presenti nello script, fornisci le informazioni esatte.\n");
        sb.Append("Se non trovi una risposta nello script o ti viene chiesto se hai il diabete, dì 'Non lo so.'.\n");
        sb.Append("Non aggiungere informazioni non richieste su altre parti del corpo.\n");
        sb.Append("Mantieni coerenza con tutti i dati forniti.\n");
        */

        // --- ROLE-PLAY ---
        sb.Append($"ROLE-PLAY:\nYou are {nomePaziente}, and you will play the role of a patient during a medical visit.\n");
        sb.Append("You will not assist the user; instead, answer all questions as if you were truly the person described.\n");
        sb.Append("Behave like a real person, responding in the first person.\n");
        sb.Append("Answer naturally, including small grammatical or punctuation mistakes.\n");
        sb.Append("Express emotions implicitly without stating them. If the doctor is rude or interrupts you, stop responding until they apologize.\n");
        sb.Append($"Use language consistent with the education level: {cartellaClinicaPazienteCorrente.DMDEDUC2}.\n");
        sb.Append("If you do not understand medical terms, say: 'I don't understand what you mean, doctor.'\n\n");

        // --- ILLNESS SCRIPT ---
        sb.Append("ILLNESS SCRIPT:\n");
        sb.Append("All your data:\n");
        sb.Append($"Personal information: Name: {nomePaziente}; Age: {cartellaClinicaPazienteCorrente.RIDAGEYR} years.\n");
        sb.Append($"Clinical data: Fasting glucose: {cartellaClinicaPazienteCorrente.LBXGLU} mg/dL; Insulin: {cartellaClinicaPazienteCorrente.LBXIN} µU/mL; Weight: {cartellaClinicaPazienteCorrente.BMXWT} kg; Height: {cartellaClinicaPazienteCorrente.BMXHT} cm; BMI: {cartellaClinicaPazienteCorrente.BMXBMI:F1}; HDL cholesterol: {cartellaClinicaPazienteCorrente.LBDHDD} mg/dL; Total cholesterol: {cartellaClinicaPazienteCorrente.LBXTC} mg/dL.\n");
        sb.Append($"Dietary data: Calories: {cartellaClinicaPazienteCorrente.DR1TKCAL} kcal; Protein: {cartellaClinicaPazienteCorrente.DR1TPROT} g; Carbohydrates: {cartellaClinicaPazienteCorrente.DR1TCARB} g; Sugars: {cartellaClinicaPazienteCorrente.DR1TSUGR} g; Fiber: {cartellaClinicaPazienteCorrente.DR1TFIBE} g; Total fat: {cartellaClinicaPazienteCorrente.DR1TTFAT} g; Saturated fat: {cartellaClinicaPazienteCorrente.DR1TSFAT} g.\n");
        sb.Append($"Physical activity: Sedentary: {cartellaClinicaPazienteCorrente.PAD680} min; Moderate: {cartellaClinicaPazienteCorrente.PAD800} min; Vigorous: {cartellaClinicaPazienteCorrente.PAD820} min.\n");
        sb.Append($"Other data: Attempts to lose weight in the past year: {cartellaClinicaPazienteCorrente.WHQ070}; Household income: {cartellaClinicaPazienteCorrente.INDFMPIR}; Ethnic origin: {cartellaClinicaPazienteCorrente.RIDRETH1}.\n\n");

        // --- ROLE INSTRUCTIONS ---
        sb.Append("ROLE INSTRUCTIONS:\n");
        sb.Append("Always respond as the patient described above.\n");
        sb.Append("If the doctor asks for clinical data from the script, provide the exact information.\n");
        sb.Append("If you can't find an answer in the script or are asked whether you have diabetes, say 'I don't know.'\n");
        sb.Append("Do not add information about other parts of the body unless requested.\n");
        sb.Append("Maintain consistency with all provided data.\n");

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
        {   
            //await per dire "aspetta che questa operazione asincrona finisca prima di continuare"
            await ttsClient.GenerateAndPlayTTSVoice(risposta, cartellaClinicaPazienteCorrente.RIAGENDR == "Male" ? MaleSpeaker : FemaleSpeaker); 
            OnPazienteFinitoDiParlare();
        }
                    
    }

    
     // Quando il paziente finisce di parlare (dopo il TTS)
    public void OnPazienteFinitoDiParlare()
    {
        IsPlayerTurn = true;
        Debug.Log("Turno del giocatore attivo");
    }

    // Quando il giocatore ha finito di parlare
    public void OnGiocatoreFinitoDiParlare()
    {
        IsPlayerTurn = false;
        Debug.Log("⏸Turno del giocatore terminato, attendo risposta del paziente...");
    }

    // Se distruggi il paziente
    public void ResetPaziente()
    {
        IsPatientSpawned = false;
        IsPlayerTurn = false;
    }


}
