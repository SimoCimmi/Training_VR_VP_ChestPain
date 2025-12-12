'''
Problema: La media non è calcolata correttamente
'''


#python "D:\Medica_Vincenzo\Valutazione_LLM\ValutatoreRisposteLLM.py"
import pandas as pd
import requests
import time
import json
import numpy as np
import os

import sys
# ==========================
# CONFIGURAZIONE
# ==========================




LM_STUDIO_URL = "http://localhost:2345/v1/chat/completions"   # Endpoint LM-Studio (default)
PATIENT_MODEL = "gemma-3-27b-it"  # modello valutatore
JUDGE_MODEL = "deepseek-r1-distill-qwen-32b"   
                 

CSV_PATH = "Clean_filteredDataset.csv"

# Domande del medico
DOMANDE = [
    "Do you know your fasting glucose and insulin levels?", # Conosci i tuoi valori di glucosio a digiuno e insulina?
    "Do you know if you have diabetes?", # Sai se hai il diabete?
    "Can you describe your typical daily meals and physical activity?", # Puoi descrivere i tuoi pasti quotidiani e l'attività fisica abituale?
    "How have you been feeling these past few days?" # Come ti sei sentito negli ultimi giorni?
]

import os
def ensure_dir_exists(path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def checkCartella(filepath):
    dir = os.path.dirname(filepath)
    if dir and not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

def make_incremental_folder(base_folder):
    """
    Crea una cartella.
    Se esiste, crea base_folder_1, base_folder_2, ...
    Restituisce il percorso della cartella creata.
    """
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        return base_folder
    
    i = 1
    while True:
        new_folder = f"{i}_{base_folder}"
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
            return new_folder
        i += 1


# ===== CREA LA CARTELLA OUTPUT =====
BASE_OUTPUT = "Reports"
OUTPUT_DIR = make_incremental_folder(BASE_OUTPUT)
print(f"Cartella per i file generata: {OUTPUT_DIR}")

# ===== LOGGER SENZA FILE INCREMENTALI =====
log_filename = os.path.join(
    OUTPUT_DIR, 
    f"report_VP-{PATIENT_MODEL}_JUDGE-{JUDGE_MODEL}.txt"
)

class TeeLogger:
    """Duplica l'output su console e su file."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        checkCartella(filename)
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Redirect output
sys.stdout = sys.stderr = TeeLogger(log_filename)

print(f"Logging attivo su file: {log_filename}")


# ==========================
# FUNZIONI UTILI
# ==========================

def build_system_prompt(p):
    nome = "Ferdinand Wilson" if p["Gender"].strip() == "Male" else "Sophie Wilson"

    prompt = f"""
ROLE-PLAY:
You are {nome}, and you will play the role of a patient during a medical visit.
You will not assist the user; instead, answer all questions as if you were truly the person described.
Behave like a real person, responding in the first person.
Respond naturally, including minor grammatical or punctuation errors.
Express emotions implicitly without stating them. If the doctor is rude, stop responding until they apologize.
Use language consistent with the following level of instruction: {p["Education_level"]}.
If you do not understand medical terms, say: "I don't understand what you mean, doctor."

ILLNESS SCRIPT:
All your data:
Personal information: 
Name: {nome}; 
Age: {p["Age"]} years.

Clinical data: 
Fasting glucose: {p["Fasting_glucose"]} mg/dL; 
Insulin: {p["Insulin_level"]} µU/mL; 
Weight: {p["Weight_kg"]} kg; 
Height: {p["Height_cm"]} cm; BMI: {p["BMI"]};
HDL cholesterol: {p["HDL_cholesterol"]} mg/dL; 
Total cholesterol: {p["Total_cholesterol"]} mg/dL.

Dietary data: 
Calories: {p["Total_calories_kcal"]} kcal; 
Protein: {p["Protein_g"]} g; 
Carbohydrates: {p["Carbohydrates_g"]} g; 
Sugars: {p["Total_sugars_g"]} g; 
Fiber: {p["Dietary_fiber_g"]} g; 
Total fat: {p["Total_fat_g"]} g; 
Saturated fat: {p["Saturated_fat_g"]} g.

Physical activity: 
Sedentary: {p["Daily_sedentary_minutes"]} min; 
Moderate: {p["Moderate_activity_minutes"]} min; 
Vigorous: {p["Vigorous_activity_minutes"]} min.

Other data: 
Have you tried to lose weight in the last year: {p["Tried_to_lose_weight_in_the_past_year"]}; 
Income to poverty threshold ratio: {p["Income_family_ratio_compared_to_the_poverty_line"]}; 
Ethnic origin: {p["Ethnic_origin"]}; 

ROLE-PLAY AND RESPONSE INSTRUCTIONS:
Always follow the ROLE-PLAY instructions.
Provide only the patient's response to the question, without adding explanations, instructions, or information about other body parts unless prompted.
The response must be on a single line, without line breaks, or other special characters.
Maintain consistency with all data provided.
"""
    return prompt



def call_llm(system_prompt, user_prompt, model):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]</s>"}
    ]
}


    start = time.time()
    print("Richiesta inviata all'LLM:")
    print(payload)
    
     
    r = requests.post(LM_STUDIO_URL, json=payload)
    latency = time.time() - start

    data = r.json()
    print("\n\nRisposta ricevuta dall'LLM: ", data)

    return {
        "text": data["choices"][0]["message"]["content"],
        "latency_sec": latency,
        "tokens_input": data["usage"]["prompt_tokens"],
        "tokens_output": data["usage"]["completion_tokens"],
        "total_tokens": data["usage"]["total_tokens"]
    }




def judge_answer(question, answer):
    #Valuta una risposta usando un LLM giudice.
    system_prompt = """
        You are an independent reviewer with experience in evaluating responses generated by virtual patients (LLMs). 
        Your task is to carefully assess the quality of the patient's answer according to the criteria listed below. 
        Base your evaluation solely on the content provided, without adding external information.

        Assign a score from 1 to 5 (integer only) for each criterion:

        1. Clinical accuracy:
        - Does the response describe behaviors, symptoms, or knowledge consistent with those of a real patient?
        - Does it avoid unrealistic or invented medical information?
        - Is it credible as something a real patient might say?

        2. Context coherence:
        - Is the response relevant to the question and appropriate for the role of a patient?
        - Does it avoid contradictions, off-topic elements, or unnecessary digressions?

        3. Completeness:
        - Does the response adequately address all essential aspects of the question?
        - Is it neither too vague nor excessively brief?

        4. Language naturalness:
        - Does the response sound spontaneous and similar to natural human speech?
        - Are any hesitations or informal expressions believable and not artificial?

        5. Explanation:
        - Provide a concise summary (1-3 sentences) that highlights the main reasons behind the evaluation.
        - The explanation should point out relevant strengths and any important weaknesses.

        Return ONLY the following JSON object (no text before or after):

        {
        "accuracy": <1-5>,
        "coherence": <1-5>,
        "completeness": <1-5>,
        "naturalness": <1-5>,
        "explanation": "<1-3 sentences summarizing the evaluation>"
        }
    """


    user_prompt = f"""
        QUESTION:
        {question}

        PATIENT ANSWER:
        {answer}

        Evaluate the answer strictly following the instructions in the system prompt.
        Return ONLY a valid JSON object.
    """
    result = call_llm(system_prompt, user_prompt, JUDGE_MODEL)
    text = result["text"]

    # cerca il primo { e l'ultimo } per estrarre il JSON
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass

    # fallback in caso di errore
    return {"error": "Invalid JSON from judge", "raw": text}







# ==========================
# PROCEDURA PRINCIPALE
# ==========================

def run_simulation():
    df = pd.read_csv(CSV_PATH)

    # converti "From 80 and up" in 80 per fare calcoli numerici
    df["Age_numeric"] = df["Age"].replace("From 80 and up", 80).astype(float).astype(int)

    def age_group(age):
        if age < 30:
            return "Young"
        elif 30 <= age <= 55:
            return "Adult"
        else:
            return "Senior"
    df["AgeGroup"] = df["Age_numeric"].apply(age_group)

    # --------------------------
    # definisci i criteri dei profili

    '''conditions = [
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "No"}
    ]'''
    
    conditions = [
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Borderline"},

        {"Gender": "Male",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Male",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Male",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "Borderline"},
 
        {"Gender": "Male",   "AgeGroup": "Senior", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Male",   "AgeGroup": "Senior", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Male",   "AgeGroup": "AdSeniorult", "Diabetes_diagnosis_positive": "Borderline"},




        {"Gender": "Female",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Female",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Female",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Borderline"},

        {"Gender": "Female",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Female",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Female",   "AgeGroup": "Adult", "Diabetes_diagnosis_positive": "Borderline"},

        {"Gender": "Female",   "AgeGroup": "Senior", "Diabetes_diagnosis_positive": "Yes"},
        {"Gender": "Female",   "AgeGroup": "Senior", "Diabetes_diagnosis_positive": "No"},
        {"Gender": "Female",   "AgeGroup": "AdSeniorult", "Diabetes_diagnosis_positive": "Borderline"}
    ]

    profiles = []

    for cond in conditions:
        subset = df
        for key, value in cond.items():
            subset = subset[subset[key] == value]
        if len(subset) > 0:
            profiles.append(subset.sample(1, random_state=42).iloc[0])
        else:
            profiles.append(None)

    # MOSTRA I PROFILI
    for i, p in enumerate(profiles, start=1):
        print(f"\n=== PROFILO {i} ===")
        if p is not None:
            print(p[["Gender", "Age", "AgeGroup", "Diabetes_diagnosis_positive", "Education_level", 
                    "Fasting_glucose", "BMI", "Moderate_activity_minutes"]])
        else:
            print("Nessun paziente che soddisfa i criteri")

    all_results =[]
    for i, profile in enumerate(profiles):
        # Simulazione LLM
        print(f"\nInizio richiesta per il profilo {i+1}:")
        if profile is None:
            print("Profilo vuoto, salto.")
            all_results.append({"profile":None, "results":[]})
            continue


        system_prompt = build_system_prompt(profile)

        profile_results = []    #Risultato del profilo
        i=0
        for question_User_Prompt in DOMANDE:
            #Risposta del VP:
            print(f"\n\n[Domanda {i} - {question_User_Prompt}] Richiesta inviata all'LLM:")
            i+=1
            response = call_llm(system_prompt, question_User_Prompt, PATIENT_MODEL)
            
            #Valutazione della risposta dal Giudice:
            evaluation = judge_answer(question_User_Prompt, response["text"])

            profile_results.append({
                "question": question_User_Prompt,
                "answer": response["text"],
                "eval": evaluation
            })
        #Salva i risultati per ogni paziente
        all_results.append({
            "profile" : profile.to_dict(),
            "results" : profile_results
        })
    return all_results



def compute_scores_table(output):
    rows = []

    for entry in output:
        prof = entry["profile"]
        results = entry["results"]

        if prof is None:
            print("Profilo vuoto, salto la riga")
            continue

        # estraggo metriche
        acc = [r["eval"]["accuracy"] for r in results if "accuracy" in r["eval"]]
        coh = [r["eval"]["coherence"] for r in results if "coherence" in r["eval"]]
        comp = [r["eval"]["completeness"] for r in results if "completeness" in r["eval"]]
        nat = [r["eval"]["naturalness"] for r in results if "naturalness" in r["eval"]]
       
       
        # media sicura con stampa dei valori e della media
        print("\n=== Metriche paziente ===")
        # Accuracy
        print(f"Valori Accuracy: {acc}")
        accuracy_mean = np.mean(acc) if acc else np.nan
        print(f"Accuracy media: {accuracy_mean}\n")

        # Coherence
        print(f"Valori Coherence: {coh}")
        coherence_mean = np.mean(coh) if coh else np.nan
        print(f"Coherence media: {coherence_mean}\n")

        # Completeness
        print(f"Valori Completeness: {comp}")
        completeness_mean = np.mean(comp) if comp else np.nan
        print(f"Completeness media: {completeness_mean}\n")

        # Naturalness
        print(f"Valori Naturalness: {nat}")
        naturalness_mean = np.mean(nat) if nat else np.nan
        print(f"Naturalness media: {naturalness_mean}\n")


        # aggiungo riga
        rows.append({
            "PatientID": int(prof.get("SEQN", -1)),  # -1 se SEQN non esiste
            "Gender": prof.get("Gender", ""),
            "AgeGroup": prof.get("AgeGroup", ""),
            "Diabetes_diagnosis_positive": prof.get("Diabetes_diagnosis_positive", ""),
            "Accuracy": accuracy_mean,
            "Coherence": coherence_mean,
            "Completeness": completeness_mean,
            "Naturalness": naturalness_mean,
        })


    return rows

def save_results_to_csv(output, filename):
    """
    Salva tutte le domande, risposte e valutazioni in un file CSV.
    Una riga = una domanda posta al paziente.
    """
    rows = []

    for entry in output:
        profile = entry["profile"]
        results = entry["results"]

        if profile is None:
            continue

        patient_id = profile.get("SEQN", None)

        for r in results:
            eval_data = r["eval"]

            rows.append({
                # Metriche singole
                "PatientID": patient_id,
                "Accuracy": eval_data.get("accuracy", None),
                "Coherence": eval_data.get("coherence", None),
                "Completeness": eval_data.get("completeness", None),
                "Naturalness": eval_data.get("naturalness", None),

                "Question": r["question"],
                "Answer": r["answer"],

                "Gender": profile.get("Gender", ""),
                "Age": profile.get("Age", ""),
                "AgeGroup": profile.get("AgeGroup", ""),
                "Diagnosis": profile.get("Diabetes_diagnosis_positive", ""),
                
                # Commento del giudice
                "Explanation": eval_data.get("explanation", ""),

                # (Opzionale) testo raw in caso di errore:
                "RawEvalError": eval_data.get("raw", "")
            })

    df_out = pd.DataFrame(rows)
    df_out.to_csv(filename, index=False, encoding="utf-8")
    print(f"\nCSV salvato correttamente in: {filename}")



def latex_table_Principali_Risposte(rows):
    """
    Genera una tabella LaTeX ottimizzata:
    - centering
    - entra nei margini
    - testo lungo va a capo nelle celle
    - include metriche numeriche tutte in una cella
    - nessun arrotondamento
    """
    table = r"""
\begin{table}[!h]
  \centering
  \resizebox{\textwidth}{!}{
    \begin{tabular}{||p{3cm} p{6cm} p{4cm} p{4cm}||}
      \hline
      Domanda & Risposta & Commento Judge & Metriche \\ [0.5ex]
      \hline\hline
"""

    for r in rows:
        # Escape caratteri speciali LaTeX
        def escape_latex(s):
            for ch in ['&', '%', '_', '#', '$', '{', '}', '~', '^', '\\']:
                s = s.replace(ch, '\\'+ch)
            return s

        question = escape_latex(r['Question'])
        answer = escape_latex(r['answer'])
        comment = escape_latex(r.get('EvaluatorComment', ''))

        # Metriche come mini-tabular nella stessa cella
        metrics = (
            r"\begin{tabular}[t]{@{}l@{}}"
            f"Acc: {r['Accuracy']} \\\\ "
            f"Coh: {r['Coherence']} \\\\ "
            f"Comp: {r['Completeness']} \\\\ "
            f"Nat.: {r['Naturalness']}"
            r"\end{tabular}"
        )

        table += f"{question} & {answer} & {comment} & {metrics} \\\\\n"
        table += "      \\hline\n"

    table += r"""    \end{tabular}
  }
  \caption{Principali risposte del modello e commenti del valutatore.}
\end{table}
"""
    return table


def latex_table_Tutte_Domande_Metriche(rows):
    """
    Genera una tabella LaTeX ottimizzata:
    - centering
    - entra nei margini
    - testo nelle celle va a capo se necessario
    """
    table = r"""
\begin{table}[!h]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{||c c c c c c c c||}
\hline
Patient & Gender & AgeGroup & Diagnosis & Acc & Coh & Comp & Nat \\ [0.5ex]
\hline\hline
"""

    for r in rows:
        table += (
            f"{r['PatientID']} & {r['Gender']} & {r['AgeGroup']} & {r['Diabetes_diagnosis_positive']} & "
            f"{r['Accuracy']:.2f} & {r['Coherence']:.2f} & {r['Completeness']:.2f} & {r['Naturalness']:.2f} \\\\\n"
        )
        table += "\\hline\n"

    table += r"""\end{tabular}
}
\caption{Valutazione media LLM-as-a-judge per ciascun paziente simulato.}
\end{table}
"""

    return table

def latex_table_Media_Metriche_Per_Colonna(rows):
    acc_sum = coh_sum = com_sum = nat_sum = 0
    count = 0

    table = r"""
\begin{table}[!h]
\centering
\begin{tabular}{||c c c c||}
\hline
Acc & Coh & Comp & Nat \\ [0.5ex]
\hline\hline
"""

    for r in rows:
        acc_sum += r['Accuracy']
        coh_sum += r['Coherence']
        com_sum += r['Completeness']
        nat_sum += r['Naturalness']
        count += 1

    acc_avg = acc_sum / count
    coh_avg = coh_sum / count
    com_avg = com_sum / count
    nat_avg = nat_sum / count

    table += (
        f"{acc_avg:.2f} & {coh_avg:.2f} & {com_avg:.2f} & {nat_avg:.2f} \\\\"
    )

    table += r"""
\hline
\end{tabular}
\caption{Medie delle metriche per tutti i pazienti selezionati.}
\label{tab:metriche_finali_pazienti}
\end{table}
"""

    return table

# ==========================
# ESECUZIONE
# ==========================

if __name__ == "__main__":
    safe_patient_model = PATIENT_MODEL.replace("/", "_").replace("\\", "_")
    safe_judge_model = JUDGE_MODEL.replace("/", "_").replace("\\", "_")

    output = run_simulation()
    print(f"Cartella per i file generata: {OUTPUT_DIR}")

    print("\n\nOutput: ")
    print(json.dumps(output, indent=4, ensure_ascii=False))

    rows = compute_scores_table(output)

    latexMetriche = latex_table_Tutte_Domande_Metriche(rows)

    name_file_exp = "Tutte_Domande_Metriche_VP-"+safe_patient_model+"_JUDGE-"+safe_judge_model+".tex"
    path = os.path.join(OUTPUT_DIR, name_file_exp)
    ensure_dir_exists(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(latexMetriche)
    print(f"Tabella LaTeX generata: {name_file_exp}")


    # crea lista di dizionari con Question, Answer e Comment
    countDomandePrese = 0
    explanation_rows = []
    for entry in output:
        for r in entry["results"]:
            eval_ = r.get("eval", {})
            if not eval_:
                continue
            avg_score = np.mean([eval_.get("accuracy",0), eval_.get("coherence",0),
                                eval_.get("completeness",0), eval_.get("naturalness",0)])
            if avg_score <= 2 or avg_score >= 4:   # criterio soglia
                countDomandePrese += 1
                if(countDomandePrese <= 8):  # prendi solo le prime 8
                   explanation_rows.append({
                        "Question": r["question"],
                        "answer": r["answer"],
                        "Accuracy": eval_.get("accuracy", 0),
                        "Coherence": eval_.get("coherence", 0),
                        "Completeness": eval_.get("completeness", 0),
                        "Naturalness": eval_.get("naturalness", 0),
                        "EvaluatorComment": eval_.get("explanation", "")
                    })
                   

    latexExplanationRisposte = latex_table_Principali_Risposte(explanation_rows)
    name_file_exp = "Principali_Risposte_VP-"+safe_patient_model+"_JUDGE-"+safe_judge_model+".tex"
    path = os.path.join(OUTPUT_DIR, name_file_exp)
    ensure_dir_exists(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(latexExplanationRisposte)
    print(f"Tabella LaTeX generata: {name_file_exp}")

    

    latexExplanationRisposte = latex_table_Media_Metriche_Per_Colonna(explanation_rows)
    name_file_exp = "Exp_Risposte_Media_Per_Colonne_Metriche_VP-"+safe_patient_model+"_JUDGE-"+safe_judge_model+".tex"
    path = os.path.join(OUTPUT_DIR, name_file_exp)
    ensure_dir_exists(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(latexExplanationRisposte)
    print(f"Tabella LaTeX generata: {name_file_exp}")

    print("Tabella LaTeX con le Metriche è stata generata: results_table_Media_Metriche_Colonna.tex")

     # Salva TUTTO in un CSV domanda-per-riga
    
    name_file_exp = "CSV_Risultati_domande_VP-"+safe_patient_model+"_JUDGE-"+safe_judge_model+".csv"
    path = os.path.join(OUTPUT_DIR, name_file_exp)
    save_results_to_csv(output, path)

    print("\n\nOutput: ")
    print(json.dumps(output, indent=4, ensure_ascii=False))
