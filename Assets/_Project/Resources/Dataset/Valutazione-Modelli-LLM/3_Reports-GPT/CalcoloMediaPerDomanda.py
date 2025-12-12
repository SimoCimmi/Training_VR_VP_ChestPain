import csv
from collections import defaultdict

input_file = "CSV_Finale_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"  # metti qui il tuo file CSV

# 1. Legge il CSV e raggruppa per domanda
data = defaultdict(lambda: {"Accuracy": [], "Coherence": [], "Completeness": [], "Naturalness": []})

with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = row["Question"]
        try:
            data[q]["Accuracy"].append(float(row["AccuracyValuUmana"]))
            data[q]["Coherence"].append(float(row["CoherenceValuUmana"]))
            data[q]["Completeness"].append(float(row["CompletenessValuUmana"]))
            data[q]["Naturalness"].append(float(row["NaturalnessValuUmana"]))
        except ValueError:
            continue  # ignora eventuali righe vuote o non valide

# 2. Calcola le medie per domanda
def mean(lst):
    return sum(lst)/len(lst) if lst else 0

table_rows = []
for q, metrics in data.items():
    acc_mean = mean(metrics["Accuracy"])
    coh_mean = mean(metrics["Coherence"])
    comp_mean = mean(metrics["Completeness"])
    nat_mean = mean(metrics["Naturalness"])
    overall_mean = mean([acc_mean, coh_mean, comp_mean, nat_mean])
    table_rows.append((q, acc_mean, coh_mean, comp_mean, nat_mean, overall_mean))

# 3. Genera tabella LaTeX
latex_table = r"""
\begin{table}[!h]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{||c c c c c c||}
\hline
Question & Acc & Coh & Comp & Nat & Media \\ [0.5ex]
\hline\hline
"""

for row in table_rows:
    question, acc, coh, comp, nat, media = row
    # escape eventuali caratteri speciali LaTeX nella domanda
    question_tex = question.replace("&", "\\&").replace("%", "\\%")
    latex_table += f"{question_tex} & {acc:.2f} & {coh:.2f} & {comp:.2f} & {nat:.2f} & {media:.2f} \\\\\n"

latex_table += r"""\hline
\end{tabular}}
\caption{Medie delle metriche per ciascuna domanda.}
\label{tab:mediePerDomanda}
\end{table}
"""

print(latex_table)
