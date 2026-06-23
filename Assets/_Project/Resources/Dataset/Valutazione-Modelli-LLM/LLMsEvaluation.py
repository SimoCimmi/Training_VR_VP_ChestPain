import pandas as pd
import json
import os
import time
from openai import OpenAI

# --- 1. CONFIGURAZIONE DEI PERCORSI INTELLIGENTE ---
# Otteniamo la cartella dove si trova fisicamente questo script (Valutazione-Modelli-LLM)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Saliamo di un livello per arrivare alla cartella 'Dataset' dove ci sono i CSV
DATASET_DIR = os.path.dirname(SCRIPT_DIR)

# Definiamo i percorsi completi
INPUT_CSV = os.path.join(DATASET_DIR, "RisposteLLMs_CSV.csv")
SYSTEM_PROMPT_FILE = os.path.join(DATASET_DIR, "Proposta di SystemPrompt per LLM-as-a-judge.txt")
USER_PROMPT_FILE = os.path.join(DATASET_DIR, "Proposta di UserPrompt per gli LLM-as-a-judge.txt")

# Creiamo la cartella dei risultati dentro 'Dataset'
OUTPUT_DIR = os.path.join(DATASET_DIR, "Reports")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "Raw_Evaluations.csv")

# Crea la cartella di output se non esiste
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 2. SETUP SERVER LM STUDIO ---
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
MODEL_NAME = "llama-3.1-8b"


# --- 3. FUNZIONI DI SUPPORTO ---
def clean_json(raw_str):
    cleaned = raw_str.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


# --- 4. ESECUZIONE PRINCIPALE ---
print(f"Verifica esistenza file...")
if not os.path.exists(INPUT_CSV):
    print(f"ERRORE: Non trovo il file CSV in: {INPUT_CSV}")
    exit()

print("Caricamento file in corso...")
df = pd.read_csv(INPUT_CSV, sep=';')

with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
    system_prompt_template = f.read()
with open(USER_PROMPT_FILE, 'r', encoding='utf-8') as f:
    user_prompt_template = f.read()

results = []
print(f"Inizio valutazione di {len(df)} risposte...")

for index, row in df.iterrows():
    # Salta le righe vuote se presenti
    if pd.isna(row['Case_ID']):
        continue

    print(f"[{index + 1}/{len(df)}] Valutando Caso {row['Case_ID']} | Modello: {row['LLM']} | Domanda: {row['Q_ID']}")

    # Costruzione Prompt
    sys_prompt = system_prompt_template.replace(
        "[PATIENT CLINICAL PROFILE]",
        f"[PATIENT CLINICAL PROFILE]\n{row['Clinical_Case']}\n"
    )

    usr_prompt = user_prompt_template.replace("{question}", str(row['Question']))
    usr_prompt = usr_prompt.replace("{answer}", str(row['Response']))

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt}
            ],
            temperature=0.1
        )

        raw_output = completion.choices[0].message.content
        json_string = clean_json(raw_output)
        json_output = json.loads(json_string)

        res_dict = {
            "Case_ID": row['Case_ID'],
            "LLM": row['LLM'],
            "Q_ID": row['Q_ID'],
            "IF": json_output.get("instruction_following", 0),
            "F": json_output.get("faithfulness", 0),
            "EAR": json_output.get("empathy", 0),
            "N": json_output.get("naturalness", 0),
            "S": json_output.get("sensibleness", 0),
            "Explanation": json_output.get("explanation", "")
        }
        results.append(res_dict)

    except Exception as e:
        print(f"  --> ERRORE alla riga {index}: {e}")
        res_dict = {
            "Case_ID": row['Case_ID'], "LLM": row['LLM'], "Q_ID": row['Q_ID'],
            "IF": 0, "F": 0, "EAR": 0, "N": 0, "S": 0,
            "Explanation": f"ERRORE: {str(e)}"
        }
        results.append(res_dict)

    time.sleep(0.1)

# Salvataggio
df_results = pd.DataFrame(results)
df_results.to_csv(OUTPUT_CSV, sep=';', index=False)
print(f"\n Valutazione completata!")
print(f"Risultati in: {OUTPUT_CSV}")