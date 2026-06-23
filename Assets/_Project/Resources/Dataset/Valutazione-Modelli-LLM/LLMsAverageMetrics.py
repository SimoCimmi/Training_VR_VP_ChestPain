import pandas as pd
import os

# --- 1. CONFIGURAZIONE PERCORSI ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(SCRIPT_DIR, "reports")
OUTPUT_FILE = os.path.join(REPORTS_DIR, "AverageMetricLLMs.csv")


def aggregate_averages():
    all_averages = []

    # Metriche da considerare per la media globale
    metrics = ['IF', 'F', 'EAR', 'N', 'S']

    print("Ricerca dei file delle medie nelle cartelle dei report...")

    # --- 2. SCANSIONE DELLE CARTELLE DEI MODELLI ---
    # Cerchiamo tutte le cartelle che finiscono con "_Reports"
    for item in os.listdir(SCRIPT_DIR):
        item_path = os.path.join(SCRIPT_DIR, item)

        if os.path.isdir(item_path) and item.endswith("_Reports"):
            llm_name = item.replace("_Reports", "")
            avg_file_name = f"{llm_name}_Averages.csv"
            avg_file_path = os.path.join(item_path, avg_file_name)

            if os.path.exists(avg_file_path):
                print(f"  > Trovato: {avg_file_name}")
                df_avg = pd.read_csv(avg_file_path, sep=';')
                all_averages.append(df_avg)
            else:
                print(f"  ! Attenzione: Non trovo {avg_file_name} in {item}")

    if not all_averages:
        print("ERRORE: Nessun file delle medie trovato. Assicurati di aver lanciato DataOrganization.py")
        return

    # --- 3. AGGREGAZIONE E CLASSIFICA ---
    # Uniamo tutti i DataFrame in uno solo
    final_df = pd.concat(all_averages, ignore_index=True)

    # Calcoliamo la Media Globale per ogni LLM (media orizzontale delle 5 metriche)
    final_df['Global_Average'] = final_df[metrics].mean(axis=1).round(2)

    # Ordiniamo in base alla Media Globale (dal più alto al più basso)
    final_df = final_df.sort_values(by='Global_Average', ascending=False)

    # --- 4. SALVATAGGIO ---
    os.makedirs(REPORTS_DIR, exist_ok=True)
    final_df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8')

    print("\n--- CLASSIFICA FINALE ---")
    print(final_df[['LLM', 'Global_Average']])
    print(f"\n✅ File aggregato creato con successo: {OUTPUT_FILE}")


if __name__ == "__main__":
    aggregate_averages()