import numpy as np
import matplotlib.pyplot as plt
import re

# ==============================
# TAB DELLA TABELLA LATEX
# ==============================
#Mistral-7b-instruct-v0.3 & 4.80 & 4.84 & 4.47 & 4.86 \\

latex_table = r"""
Qwen2.5-coder-14b & 4.27 & 4.44 & 4.11 & 4.55 \\
Gpt-oss-20b & 4.55 & 4.88 & 4.17 & 4.81 \\
Gemma-3-27b-it & 4.61 & 4.84 & 3.98 & 4.91 \\
Gemma-3-12b & 4.42 & 4.80 & 3.55 & 4.88 \\
"""

# ==============================
# PARSING DELLA TABELLA
# ==============================
models = {}

for line in latex_table.split("\n"):
    line = line.strip()
    if not line or line.startswith("\\"):
        continue

    line = line.replace("\\\\", "").strip()

    parts = [p.strip() for p in line.split("&")]
    if len(parts) != 5:
        continue

    model = parts[0]
    values = list(map(float, parts[1:]))

    # Calcolo media
    mean_value = np.mean(values)

    # Salvataggio valori + media
    models[model] = {
        "metrics": values,
        "mean": mean_value
    }

# ==============================
# ORDINAMENTO PER MEDIA
# ==============================
sorted_models = dict(sorted(models.items(), key=lambda x: x[1]["mean"], reverse=True))

print("Classifica modelli (dal migliore):")
for m, data in sorted_models.items():
    print(f"{m} → Media: {data['mean']:.4f}")

# ==============================
# GENERAZIONE NUOVA TABELLA LATEX
# ==============================
latex_output = "\\begin{table}[!h]\n\\centering\n"
latex_output += "\\begin{tabular}{||c c c c c c||}\n"
latex_output += "\\hline\n"
latex_output += "Modello & Acc & Coh & Comp & Nat & Media \\\\\n"
latex_output += "\\hline\\hline\n"

for model, data in sorted_models.items():
    acc, coh, comp, nat = data["metrics"]
    mean_val = data["mean"]
    latex_output += f"{model} & {acc:.2f} & {coh:.2f} & {comp:.2f} & {nat:.2f} & {mean_val:.2f} \\\\\n"
    latex_output += "\\hline\n"

latex_output += "\\end{tabular}\n"
latex_output += "\\caption{Metriche dei modelli con media complessiva e ordinamento dal migliore al peggiore.}\n"
latex_output += "\\end{table}"

print("\n=== TABELLA LATEX ORDINATA ===\n")
print(latex_output)

# ==============================
# GRAFICO RADAR
# ==============================
labels = ['Acc', 'Coh', 'Comp ', 'Nat']

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
angles = np.concatenate((angles, [angles[0]]))  # chiusura poligono

plt.figure(figsize=(6, 6))

for model, data in sorted_models.items():
    values = np.array(data["metrics"])
    values = np.concatenate((values, [values[0]]))
    plt.polar(angles, values, marker='o', label=model)

plt.xticks(angles[:-1], labels)
plt.ylim(0, 5)
plt.title("Confronto LLM sulle metriche")
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.show()