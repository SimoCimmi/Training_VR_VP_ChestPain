import pandas as pd
import os

# --- 1. CONFIGURAZIONE PERCORSI ---
# Lo script si trova in: .../Valutazione-Modelli-LLM/Final_Reports/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# La cartella principale (Valutazione-Modelli-LLM) è il genitore di Final_Reports

INPUT_CSV = os.path.join(SCRIPT_DIR, "Final_Reports/Raw_HumanEvaluations_CSV.csv")


def organize_human_data():
    if not os.path.exists(INPUT_CSV):
        print(f"ERRORE: Non trovo il file {INPUT_CSV}")
        return

    # --- 2. CARICAMENTO DATI ---
    print("Caricamento valutazioni umane...")
    df = pd.read_csv(INPUT_CSV, sep=';')

    # Pulizia nomi colonne e righe
    df.columns = df.columns.str.strip()
    df['LLM'] = df['LLM'].str.strip()

    llms = df['LLM'].dropna().unique()
    metrics = ['IF', 'F', 'EAR', 'N', 'S']

    print(f"Modelli valutati dagli umani: {', '.join(llms)}")

    for llm in llms:
        print(f"\n--- Elaborazione Umana per {llm} ---")

        # Puntiamo alla cartella GIÀ ESISTENTE nella directory (es. .../Valutazione-Modelli-LLM/Gema_Reports)
        folder_name = f"{llm}_Reports"
        llm_dir = os.path.join(SCRIPT_DIR, folder_name)

        df_llm = df[df['LLM'] == llm]

        # A. Salvataggio valutazioni singole umane nella cartella del modello
        eval_file = os.path.join(llm_dir, f"Human_{llm}_Evaluations.csv")
        df_llm.to_csv(eval_file, sep=';', index=False, encoding='utf-8')
        print(f"  > Creato: {folder_name}/Human_{llm}_Evaluations.csv")

        # B. Calcolo delle medie umane
        averages = df_llm[metrics].mean().to_frame().transpose()
        averages = averages.round(2)
        averages.insert(0, 'LLM', llm)

        avg_file = os.path.join(llm_dir, f"Human_{llm}_Averages.csv")
        averages.to_csv(avg_file, sep=';', index=False, encoding='utf-8')
        print(f"  > Creato: {folder_name}/Human_{llm}_Averages.csv")

    print("\n Organizzazione dati umani completata nelle cartelle esistenti!")


if __name__ == "__main__":
    organize_human_data()