import pandas as pd
import os

# --- 1. CONFIGURAZIONE PERCORSI ---
# Lo script si trova in: .../Valutazione-Modelli-LLM/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Il file Raw_Evaluations.csv si trova nella sottocartella 'reports'
INPUT_DIR = os.path.join(SCRIPT_DIR, "reports")
INPUT_CSV = os.path.join(INPUT_DIR, "Raw_Evaluations.csv")


def organize_and_calculate_averages():
    # Verifica esistenza file
    if not os.path.exists(INPUT_CSV):
        print(f"ERRORE: Non trovo il file {INPUT_CSV}")
        print("Assicurati di aver spostato Raw_Evaluations.csv nella cartella 'reports'.")
        return

    # --- 2. CARICAMENTO DATI ---
    print("Caricamento dati in corso...")
    df = pd.read_csv(INPUT_CSV, sep=';')

    # Pulizia: rimuoviamo eventuali spazi bianchi dai nomi degli LLM (es. "Mistral " -> "Mistral")
    df['LLM'] = df['LLM'].str.strip()

    # Lista degli LLM unici presenti nel file
    llms = df['LLM'].unique()

    # Metriche da calcolare
    metrics = ['IF', 'F', 'EAR', 'N', 'S']

    print(f"Modelli individuati: {', '.join(llms)}")

    for llm in llms:
        print(f"\n--- Elaborazione {llm} ---")

        # Creazione cartella del modello (es. Mistral_Reports)
        folder_name = f"{llm}_Reports"
        llm_dir = os.path.join(SCRIPT_DIR, folder_name)
        os.makedirs(llm_dir, exist_ok=True)

        # Filtraggio dati per il singolo modello
        df_llm = df[df['LLM'] == llm]

        # A. Salvataggio valutazioni singole
        eval_file = os.path.join(llm_dir, f"{llm}_Evaluations.csv")
        df_llm.to_csv(eval_file, sep=';', index=False, encoding='utf-8')
        print(f"  > Creato: {llm}_Evaluations.csv")

        # B. Calcolo delle medie
        # Calcoliamo la media solo per le colonne delle metriche
        averages = df_llm[metrics].mean().to_frame().transpose()

        # Arrotondiamo a 2 decimali per pulizia
        averages = averages.round(2)

        # Aggiungiamo una colonna col nome del modello per riferimento
        averages.insert(0, 'LLM', llm)

        # Salvataggio medie
        avg_file = os.path.join(llm_dir, f"{llm}_Averages.csv")
        averages.to_csv(avg_file, sep=';', index=False, encoding='utf-8')
        print(f"  > Creato: {llm}_Averages.csv (Medie calcolate)")

    print("\n Organizzazione completata! Le cartelle dei report sono pronte.")


if __name__ == "__main__":
    organize_and_calculate_averages()