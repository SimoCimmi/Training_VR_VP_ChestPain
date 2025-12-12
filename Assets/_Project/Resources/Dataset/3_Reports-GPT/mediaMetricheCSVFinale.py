import pandas as pd

# === Percorso del file CSV ===
csv_path = "CSV_Finale_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"   # <-- sostituisci con il tuo percorso reale

# === Nome del modello da mostrare nella tabella ===
nome_modello = "Gpt-oss-20b"

# === Lettura CSV ===
df = pd.read_csv(csv_path)

# === Conversione colonne in numerico (sicurezza) ===
df["AccuracyValuUmana"] = pd.to_numeric(df["AccuracyValuUmana"], errors="coerce")
df["CoherenceValuUmana"] = pd.to_numeric(df["CoherenceValuUmana"], errors="coerce")
df["CompletenessValuUmana"] = pd.to_numeric(df["CompletenessValuUmana"], errors="coerce")
df["NaturalnessValuUmana"] = pd.to_numeric(df["NaturalnessValuUmana"], errors="coerce")

# === Calcolo delle medie ===
acc_mean = df["AccuracyValuUmana"].mean()
coh_mean = df["CoherenceValuUmana"].mean()
comp_mean = df["CompletenessValuUmana"].mean()
nat_mean = df["NaturalnessValuUmana"].mean()

# === Creazione tabella LaTeX ===
latex_table = f"""
\\begin{{table}}[!h]
  \\centering
  \\begin{{tabular}}{{||c c c c c||}}
    \\hline
    Modello & Acc & Coh & Comp & Nat \\\\ [0.5ex]
    \\hline\\hline
    {nome_modello} & {acc_mean:.2f} & {coh_mean:.2f} & {comp_mean:.2f} & {nat_mean:.2f} \\\\
    \\hline
  \\end{{tabular}}
  \\caption{{Medie delle metriche della valutazione umana per tutti i VP.}}
  \\label{{tab:metriche_finali_val_umana_pazienti}}
\\end{{table}}
"""

# === Stampa risultato ===
print(latex_table)
