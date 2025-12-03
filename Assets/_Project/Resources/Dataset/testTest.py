import csv

# --- FILE E MODELLI ---
files = {
    "Gemma-27B": r"1_Reports-Gemma-27b\CSV_Valutazione_Umana_Risultati_domande_VP-gemma-3-27b-it_JUDGE-deepseek-r1-distill-qwen-32b.csv",
    "GPT-OpenAI-20B": r"3_Reports-GPT\CSV_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"
}

# --- FUNZIONE PER CALCOLARE LE MEDIE ---
def calcola_medie(csv_file):
    accuracy_list = []
    coherence_list = []
    completeness_list = []
    naturalness_list = []

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                accuracy_list.append(float(row['AccuracyValuUmana'].strip()))
                coherence_list.append(float(row['CoherenceValuUmana'].strip()))
                completeness_list.append(float(row['CompletenessValuUmana'].strip()))
                naturalness_list.append(float(row['NaturalnessValuUmana'].strip()))
            except:
                continue

    def mean(lst):
        return sum(lst) / len(lst) if lst else 0

    return {
        "Accuracy": mean(accuracy_list),
        "Coherence": mean(coherence_list),
        "Completeness": mean(completeness_list),
        "Naturalness": mean(naturalness_list)
    }

# --- CALCOLO PER TUTTI I MODELLI ---
results = {}
for model_name, file_path in files.items():
    results[model_name] = calcola_medie(file_path)

# --- ORDINAMENTO PER MEDIA COMPLESSIVA (Accuracy+Coherence+Completeness+Naturalness) ---
sorted_models = sorted(
    results.items(),
    key=lambda x: sum(x[1].values()),
    reverse=True
)

# --- STAMPA CONSOLE ---
print("RISULTATI ORDINATI (dal migliore al peggiore):\n")
for model, metrics in sorted_models:
    print(f"Modello: {model}")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print(f"  Media totale: {sum(metrics.values())/4:.2f}")
    print()

# --- GENERAZIONE TABELLA LATEX ---
latex_table = r"""
\begin{table}[!h]
\centering
\begin{tabular}{||c|c|c|c|c||}
\hline
Modello & Accuracy & Coherence & Completeness & Naturalness \\
\hline\hline
"""

for model, metrics in sorted_models:
    latex_table += f"{model} & {metrics['Accuracy']:.2f} & {metrics['Coherence']:.2f} & {metrics['Completeness']:.2f} & {metrics['Naturalness']:.2f} \\\\\n"

latex_table += r"""\hline
\end{tabular}
\caption{Confronto delle metriche di valutazione umana per i due modelli.}
\end{table}
"""

print("\nTABELLONE LATEX:\n")
print(latex_table)
