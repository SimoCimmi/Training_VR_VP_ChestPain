import pandas as pd
import os

# --- 1. CONFIGURAZIONE PERCORSI ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "Final_Reports/HumanAverageMetrics.csv")


def aggregate_human_averages():
    all_averages = []
    metrics = ['IF', 'F', 'EAR', 'N', 'S']

    print("Aggregazione delle medie umane dalle cartelle dei modelli...")

    # Cerchiamo i file delle medie umane dentro le cartelle "_Reports" del livello superiore
    for item in os.listdir(SCRIPT_DIR):
        item_path = os.path.join(SCRIPT_DIR, item)

        if os.path.isdir(item_path) and item.endswith("_Reports"):
            llm_name = item.replace("_Reports", "")
            avg_file_name = f"Human_{llm_name}_Averages.csv"
            avg_file_path = os.path.join(item_path, avg_file_name)

            if os.path.exists(avg_file_path):
                print(f"  > Trovato: {item}/{avg_file_name}")
                df_avg = pd.read_csv(avg_file_path, sep=';')
                all_averages.append(df_avg)

    if not all_averages:
        print("ERRORE: Nessun file delle medie umane trovato. Lancia prima HumanDataOrganization.py")
        return

    # Unione e calcolo classifica globale
    final_df = pd.concat(all_averages, ignore_index=True)
    final_df['Global_Average'] = final_df[metrics].mean(axis=1).round(2)
    final_df = final_df.sort_values(by='Global_Average', ascending=False)

    final_df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8')

    print("\n--- CLASSIFICA FINALE (VALUTATORI UMANI) ---")
    print(final_df[['LLM', 'Global_Average']])
    print(f"\n File aggregato umano salvato in: {OUTPUT_FILE}")


if __name__ == "__main__":
    aggregate_human_averages()