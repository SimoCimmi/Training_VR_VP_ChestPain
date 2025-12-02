import csv

# Nome del file CSV

csv_file = r"Reports_VP-google_gemma-3-27b_JUDGE-deepseek-r1-distill-qwen-32b\CSV_Risultati_domande_VP-google_gemma-3-27b_JUDGE-deepseek-r1-distill-qwen-32b.csv"

# Liste per accumulare i valori delle metriche

accuracy_list = []
coherence_list = []
completeness_list = []
naturalness_list = []

# Lettura del CSV

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Conversione in float (gestisce eventuali spazi)
        try:
            accuracy_list.append(float(row['Accuracy'].strip()))
            coherence_list.append(float(row['Coherence'].strip()))
            completeness_list.append(float(row['Completeness'].strip()))
            naturalness_list.append(float(row['Naturalness'].strip()))
        except ValueError:
            continue  # ignora righe con dati non validi

# Calcolo medie

def mean(lst):
    return sum(lst) / len(lst) if lst else 0

acc_mean = mean(accuracy_list)
coh_mean = mean(coherence_list)
com_mean = mean(completeness_list)
nat_mean = mean(naturalness_list)

# Stampa in console

print(f"Medie metriche:")
print(f"Accuracy: {acc_mean:.2f}")
print(f"Coherence: {coh_mean:.2f}")
print(f"Completeness: {com_mean:.2f}")
print(f"Naturalness: {nat_mean:.2f}")

# Stampa in formato LaTeX

latex_table = f"""
\begin{{table}}[!h]
\centering
\begin{{tabular}}{{||c c c c||}}
\hline
Acc & Coh & Comp & Nat \\ [0.5ex]
\hline\hline
{acc_mean:.2f} & {coh_mean:.2f} & {com_mean:.2f} & {nat_mean:.2f} \\
\hline
\end{{tabular}}
\caption{{Medie delle metriche per tutti i pazienti.}}
\end{{table}}
"""

print("\nTabella LaTeX:\n")
print(latex_table)
