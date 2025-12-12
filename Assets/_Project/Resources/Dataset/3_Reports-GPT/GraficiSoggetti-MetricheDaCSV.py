import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === Percorso dove salvare i PDF ===
path = r"C:\Users\vince\Documents\Vincenzo Medica\UNISA Google Drive\Tesi\SchemiTesi\GraficiValutazioneLLM-CSV\\"

# Crea la cartella se non esiste
os.makedirs(path, exist_ok=True)

# === LETTURA CSV ===
csv_file = "CSV_Finale_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv" 

df_csv = pd.read_csv(csv_file)

# Seleziona solo le colonne necessarie e rinominale
df = df_csv[["PatientID", "Gender", "AgeGroup", "Diagnosis", 
             "AccuracyValuUmana", "CoherenceValuUmana", "CompletenessValuUmana", "NaturalnessValuUmana"]].copy()

df.rename(columns={
    "PatientID": "Patient",
    "AccuracyValuUmana": "Acc",
    "CoherenceValuUmana": "Coh",
    "CompletenessValuUmana": "Comp",
    "NaturalnessValuUmana": "Nat"
}, inplace=True)

# === GRAFICO 1: Boxplot Completezza per Fascia Età ===
plt.figure(figsize=(8,6))
df.boxplot(column="Comp", by="AgeGroup")
plt.title("Distribuzione della Completezza per Fascia di Età")
plt.suptitle("")
plt.ylabel("Comp")
plt.xlabel("Fascia di età")

plt.savefig(path + "boxplot_completezza_per_eta.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO 4: Boxplot metriche ===
plt.figure(figsize=(10,6))
df[["Acc","Coh","Comp","Nat"]].boxplot()
plt.ylabel("Punteggio")
plt.title("Distribuzione dei punteggi per metrica")

plt.savefig(path + "boxplot_metriche.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO 6: Medie per gruppo di età (per metrica) ===
group_age = df.groupby("AgeGroup")[["Acc","Coh","Comp","Nat"]].mean()
ax = group_age.plot(kind="bar", figsize=(10,6))
plt.ylabel("Punteggio medio")
plt.title("Punteggio medio per metrica e gruppo di età")
plt.xticks(rotation=0)

for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", label_type='edge', padding=3)

plt.legend(title="Metriche", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(path + "punteggio_medio_metrica_eta.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO 6.2: Medie per genere (per metrica) ===
group_gender = df.groupby("Gender")[["Acc","Coh","Comp","Nat"]].mean()
ax = group_gender.plot(kind="bar", figsize=(10,6))
plt.ylabel("Punteggio medio")
plt.title("Punteggio medio per metrica e genere")
plt.xticks(rotation=0)

for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", label_type='edge', padding=3)

plt.legend(title="Metriche", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(path + "punteggio_medio_metrica_genere.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO 7: Completezza ordinata ===
df_sorted = df.sort_values(by="Comp")
plt.figure(figsize=(12,6))
plt.bar(df_sorted["Patient"].astype(str), df_sorted["Comp"])
plt.xticks(rotation=90)
plt.ylabel("Comp")
plt.title("Completezza per paziente (ordinati dal più basso)")
plt.tight_layout()
plt.savefig(path + "completezza_ordinata.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO: Metriche per Genere (tutte le metriche nello stesso grafico) ===
group_gender = df.groupby("Gender")[["Acc", "Coh", "Comp", "Nat"]].mean()
plt.figure(figsize=(10,6))
ax = group_gender.plot(kind="bar", figsize=(10,6))
plt.title("Metriche medie per Genere")
plt.ylabel("Punteggio medio")
plt.xlabel("Genere")
plt.xticks(rotation=0)
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2)
plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()
plt.savefig(path + "metriche_per_genere.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === GRAFICO: Metriche per Diagnosi ===
order = ["Yes", "No", "Borderline"]
df["Diagnosis"] = pd.Categorical(df["Diagnosis"], categories=order, ordered=True)
group_diag = df.groupby("Diagnosis")[["Acc", "Coh", "Comp", "Nat"]].mean()

plt.figure(figsize=(10,6))
ax = group_diag.plot(kind="bar", figsize=(10,6))
plt.title("Metriche medie per Diagnosi")
plt.ylabel("Punteggio medio")
plt.xlabel("Diagnosi")
plt.xticks(rotation=0)
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2)
plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()
plt.savefig(path + "metriche_per_diagnosi.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === Statistiche ===
stats = df[["Acc","Coh","Comp","Nat"]].agg(["mean","std","min","max"])
print(stats)
