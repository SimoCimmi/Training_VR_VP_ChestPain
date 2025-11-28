'''
TEMPI DI EXE:
USANDO: PATIENT_MODEL = "gemma-3-27b-it"  + JUDGE_MODEL = "deepseek-r1-distill-qwen-32b"  
START: 2025-11-24 11:30:00
FINISH: 2025-11-24 12:54:16
TOT: 1:24

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

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"   # Endpoint LM-Studio (default)
PATIENT_MODEL = "meta-llama-3-8b-instruct"                      # modello valutatore
JUDGE_MODEL = "meta-llama-3-8b-instruct"   
                 # modello paziente

CSV_PATH = "Clean_filteredDataset.csv"

# Domande del medico
DOMANDE = [
    "Do you know your fasting glucose and insulin levels?", # Conosci i tuoi valori di glucosio a digiuno e insulina?
    #"Do you know if you have diabetes?",#, # Sai se hai il diabete?
    #"Can you describe your typical daily meals and physical activity?", # Puoi descrivere i tuoi pasti quotidiani e l'attività fisica abituale?
    #"How have you been feeling these past few days?" # Come ti sei sentito negli ultimi giorni?
]


def make_incremental_file(base_name):
    """Se base_name esiste, crea base_name_1.txt, base_name_2.txt, ecc."""
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    i = 1
    while True:
        new_name = f"{i}_{name}{ext}"
        if not os.path.exists(new_name):
            return new_name
        i += 1

class TeeLogger:
    """Duplica l'output su console e su file."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

log_filename = make_incremental_file("report_VP-"+PATIENT_MODEL+"_JUDGE-"+JUDGE_MODEL+".txt")
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
Answer naturally, including small grammatical or punctuation mistakes.
Express emotions implicitly without stating them. If the doctor is rude, stop responding until they apologize.
Use language consistent with the education level: {p["Education_level"]}.
If you do not understand medical terms, say: "I don't understand what you mean, doctor."

ILLNESS SCRIPT:
All your data:
Personal information: Name: {nome}; Age: {p["Age"]} years.
Clinical data: Fasting glucose: {p["Fasting_glucose"]} mg/dL; Insulin: {p["Insulin_level"]} µU/mL; 
Weight: {p["Weight_kg"]} kg; Height: {p["Height_cm"]} cm; BMI: {p["BMI"]};
HDL cholesterol: {p["HDL_cholesterol"]} mg/dL; Total cholesterol: {p["Total_cholesterol"]} mg/dL.
Dietary data: Calories: {p["Total_calories_kcal"]} kcal; Protein: {p["Protein_g"]} g; 
Carbohydrates: {p["Carbohydrates_g"]} g; Sugars: {p["Total_sugars_g"]} g; Fiber: {p["Dietary_fiber_g"]} g; 
Total fat: {p["Total_fat_g"]} g; Saturated fat: {p["Saturated_fat_g"]} g.
Physical activity: Sedentary: {p["Daily_sedentary_minutes"]} min; 
Moderate: {p["Moderate_activity_minutes"]} min; Vigorous: {p["Vigorous_activity_minutes"]} min.
Other data: Tried to lose weight: {p["Tried_to_lose_weight_in_the_past_year"]}; 
Income ratio vs poverty line: {p["Income_family_ratio_compared_to_the_poverty_line"]}; 
Ethnic origin: {p["Ethnic_origin"]}; 
Diabetes diagnosis positive: {p["Diabetes_diagnosis_positive"]}.

ROLE INSTRUCTIONS:

Always answer following the instructions described above in ROLE-PLAY.
If the doctor asks for clinical data from the script, provide the exact information.
If you can't find an answer in the script or are asked whether you have diabetes, say "I don't know."
Do not add information about other parts of the body unless requested.
Maintain consistency with all provided data.

"""
    return prompt



def call_llm(system_prompt, user_prompt, model):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        #{"role": "user", "content": f"System Prompt: {system_prompt} \n\n User prompt:{user_prompt}"}
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
        - Provide a concise summary (1–3 sentences) that highlights the main reasons behind the evaluation.
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

    conditions = [
        {"Gender": "Male",   "AgeGroup": "Young", "Diabetes_diagnosis_positive": "Yes"},
    ]
    
    '''conditions = [
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
    ]'''

    profiles = []

    for cond in conditions:
        subset = df
        for key, value in cond.items():
            subset = subset[subset[key] == value]
        if len(subset) > 0:
            profiles.append(subset.sample(1).iloc[0])
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

def latex_table_Explanation_Risposte(rows):
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


def latex_table_Metriche(rows):
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
    output = run_simulation()
    print("\n\nOutput: ")
    print(json.dumps(output, indent=4, ensure_ascii=False))

    rows = compute_scores_table(output)

    latexMetriche = latex_table_Metriche(rows)

    # salva in file
    with open("results_table_Metriche.tex", "w", encoding="utf-8") as f:
        f.write(latexMetriche)

    print("Tabella LaTeX con le Metriche è stata generata: results_table_Metriche.tex")


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
    latexExplanationRisposte = latex_table_Explanation_Risposte(explanation_rows)

    # salva in file
    name_file_exp = make_incremental_file("Exp_Risposte_VP-"+PATIENT_MODEL+"_JUDGE-"+JUDGE_MODEL+".tex")
    with open(name_file_exp, "w", encoding="utf-8") as f:
        f.write(latexExplanationRisposte)
    print(f"Tabella LaTeX generata: {name_file_exp}")
    
    name_file_exp = make_incremental_file("Exp_Risposte_Media_Metriche_VP-"+PATIENT_MODEL+"_JUDGE-"+JUDGE_MODEL+".tex")
    with open(name_file_exp, "w", encoding="utf-8") as f:
        f.write(latexExplanationRisposte)
    print(f"Tabella LaTeX generata: {name_file_exp}")


    name_file_exp = make_incremental_file("Exp_Risposte_Media_Per_Colonne_Metriche_VP-"+PATIENT_MODEL+"_JUDGE-"+JUDGE_MODEL+".tex")
    with open(name_file_exp, "w", encoding="utf-8") as f:
        f.write(latexExplanationRisposte)
    print(f"Tabella LaTeX generata: {name_file_exp}")

    print("Tabella LaTeX con le Metriche è stata generata: results_table_Media_Metriche_Colonna.tex")
