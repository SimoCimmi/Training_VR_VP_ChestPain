import csv

# --- FILE DEI DUE MODELLI ---
files = {
    "Gemma-3-27b-it": r"1_Reports-Gemma-27b\CSV_Finale_Valutazione_Umana_Risultati_domande_VP-gemma-3-27b-it_JUDGE-deepseek-r1-distill-qwen-32b.csv",
    "Gpt-oss-20b": r"3_Reports-GPT\CSV_Finale_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"
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
results = {
    model_name: calcola_medie(file_path)
    for model_name, file_path in files.items()
}

# --- ORDINAMENTO PER MEDIA COMPLESSIVA ---
sorted_models = sorted(
    results.items(),
    key=lambda x: sum(x[1].values()),
    reverse=True
)

# --- STAMPA CONSOLE ---
print("RISULTATI ORDINATI (dal migliore al peggiore):\n")
for model, metrics in sorted_models:
    media_totale = sum(metrics.values()) / 4
    print(f"Modello: {model}")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print(f"  Media totale: {media_totale:.2f}\n")

# --- GENERAZIONE TABELLA LATEX ---
latex_table = r"""
\begin{table}[!h]
  \centering
  \begin{tabular}{||c c c c c c||}
    \hline
Modello & Acc & Coh & Comp & Nat & Media \\
\hline\hline
"""

for model, metrics in sorted_models:
    media = sum(metrics.values()) / 4
    latex_table += (
        f"{model} & "
        f"{metrics['Accuracy']:.2f} & "
        f"{metrics['Coherence']:.2f} & "
        f"{metrics['Completeness']:.2f} & "
        f"{metrics['Naturalness']:.2f} & "
        f"{media:.2f} \\\\\n"
    )

latex_table += r"""\hline
\end{tabular}
\caption{Confronto delle metriche della valutazione umana per i modelli.}
\label{tab:valutazioneUmanaLlm}
\end{table}
"""

print("\nTABELLONE LATEX:\n")
print(latex_table)

