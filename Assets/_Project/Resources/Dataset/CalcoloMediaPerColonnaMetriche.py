import re
import numpy as np

latex_table = r"""
\begin{table}[!h]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{||c c c c c c c c||}
\hline
Patient & Gender & AgeGroup & Diagnosis & Acc & Coh & Comp & Nat \\ [0.5ex]
\hline\hline
135140 & Male & Young & Yes & 4.25 & 4.75 & 4.00 & 5.00 \\
\hline
136641 & Male & Young & No & 4.75 & 4.75 & 3.75 & 4.75 \\
\hline
132602 & Male & Young & Borderline & 4.50 & 4.75 & 4.50 & 5.00 \\
\hline
137037 & Male & Adult & Yes & 4.50 & 4.50 & 4.00 & 4.50 \\
\hline
137870 & Male & Adult & No & 4.75 & 4.75 & 4.75 & 5.00 \\
\hline
131546 & Male & Adult & Borderline & 4.25 & 4.50 & 3.75 & 5.00 \\
\hline
136691 & Male & Senior & Yes & 4.75 & 4.75 & 4.25 & 5.00 \\
\hline
138563 & Male & Senior & No & 4.75 & 4.75 & 4.00 & 5.00 \\
\hline
137112 & Female & Young & Yes & 4.50 & 4.75 & 4.50 & 4.75 \\
\hline
137856 & Female & Young & No & 4.75 & 4.50 & 4.00 & 4.50 \\
\hline
136670 & Female & Young & Borderline & 4.75 & 4.75 & 4.00 & 5.00 \\
\hline
138374 & Female & Adult & Yes & 4.25 & 4.50 & 3.75 & 5.00 \\
\hline
139172 & Female & Adult & No & 4.50 & 5.00 & 4.00 & 5.00 \\
\hline
133751 & Female & Adult & Borderline & 4.50 & 4.75 & 4.25 & 5.00 \\
\hline
138162 & Female & Senior & Yes & 4.25 & 5.00 & 4.25 & 4.50 \\
\hline
137302 & Female & Senior & No & 4.25 & 4.75 & 4.50 & 4.75 \\
\hline
\end{tabular}
}
\caption{Valutazione media LLM-as-a-judge per ciascun paziente simulato.}
\end{table}
"""

# Estrai le righe della tabella con valori
pattern = re.compile(r'^\s*\d+ & .*? & ([-+]?\d*\.\d+) & ([-+]?\d*\.\d+) & ([-+]?\d*\.\d+) & ([-+]?\d*\.\d+)\s*\\\\', re.MULTILINE)
matches = pattern.findall(latex_table)

# Converti in float e metti in array numpy
data = np.array(matches, dtype=float)

# Calcola la media per colonna
medie = np.mean(data, axis=0)

# Stampa tabella LaTeX con medie
print(r"\begin{table}[!h]")
print(r"\centering")
print(r"\begin{tabular}{||c c c c||}")
print(r"\hline")
print("Acc & Coh & Comp & Nat \\\\ [0.5ex]")
print(r"\hline\hline")
print(f"{medie[0]:.2f} & {medie[1]:.2f} & {medie[2]:.2f} & {medie[3]:.2f} \\\\")
print(r"\hline")
print(r"\end{tabular}")
print(r"\caption{Medie delle metriche per tutti i pazienti.}")
print(r"\end{table}")
