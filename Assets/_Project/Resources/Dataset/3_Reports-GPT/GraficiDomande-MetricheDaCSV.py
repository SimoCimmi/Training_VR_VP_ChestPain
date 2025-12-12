import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

# === Percorso dove salvare i PDF ===
path = r"C:\Users\vince\Documents\Vincenzo Medica\UNISA Google Drive\Tesi\SchemiTesi\GraficiDomande-MetricheLLM-CSV\\"

# Crea la cartella se non esiste
os.makedirs(path, exist_ok=True)

# === LETTURA CSV ===
csv_file = "CSV_Finale_Valutazione_Umana_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"
df_csv = pd.read_csv(csv_file)

# Seleziona solo le colonne necessarie e rinominale
df = df_csv[["PatientID", "Gender", "AgeGroup", "Diagnosis", "Question",
             "AccuracyValuUmana", "CoherenceValuUmana", "CompletenessValuUmana", "NaturalnessValuUmana"]].copy()

df.rename(columns={
    "PatientID": "Patient",
    "AccuracyValuUmana": "Acc",
    "CoherenceValuUmana": "Coh",
    "CompletenessValuUmana": "Comp",
    "NaturalnessValuUmana": "Nat"
}, inplace=True)


# === MAPPATURA FISSA DELLE DOMANDE A D1–D4 ===
question_map = {
    "Do you know your fasting glucose and insulin levels?": "D1",
    "Do you know if you have diabetes?": "D2",
    "Can you describe your typical daily meals and physical activity?": "D3",
    "How have you been feeling these past few days?": "D4"
}

df["QuestionShort"] = df["Question"].map(question_map)

# === 2. Media delle metriche per domanda ===
group_question = df.groupby("QuestionShort")[["Acc","Coh","Comp","Nat"]].mean()
ax = group_question.plot(kind="bar", figsize=(12,6), width=0.6)
plt.title("Punteggio medio delle metriche per domanda")
plt.ylabel("Punteggio medio")
plt.xlabel("Domande")
plt.xticks(rotation=0, ha="center")
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2)
plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()
plt.savefig(path + "N_media_metriche_per_domanda.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === 3. Heatmap di correlazione ===
corr_question = df.groupby("QuestionShort")[["Acc","Coh","Comp","Nat"]].mean().corr()
plt.figure(figsize=(6,5))
sns.heatmap(corr_question, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlazione tra metriche (medie per domanda)")
plt.tight_layout()
plt.savefig(path + "N_correlazione_metriche_per_domanda.pdf", format="pdf", bbox_inches="tight")
plt.close()


# === 1. Boxplot delle metriche per domanda ===
plt.figure(figsize=(12,6))
df_box = df.melt(id_vars=["QuestionShort"], value_vars=["Acc","Coh","Comp","Nat"],
                 var_name="Metrica", value_name="Punteggio")
sns.boxplot(x="QuestionShort", y="Punteggio", hue="Metrica", data=df_box)
plt.title("Distribuzione delle metriche per domanda")
plt.xlabel("Domande")
plt.ylabel("Punteggio")
plt.xticks(rotation=0, ha="center")
plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()
plt.savefig(path + "boxplot_metriche_per_domanda.pdf", format="pdf", bbox_inches="tight")
plt.close()




# === 4. Scatter plot: Acc vs Comp per domanda ===
plt.figure(figsize=(10,6))
for q in df["QuestionShort"].unique():
    subset = df[df["QuestionShort"] == q]
    plt.scatter(subset["Acc"], subset["Comp"], label=q, alpha=0.7, s=80)
plt.xlabel("Accuratezza (Acc)")
plt.ylabel("Completezza (Comp)")
plt.title("Correlazione Acc vs Comp per domanda")
plt.legend(title="Domande", bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.savefig(path + "correlazione_acc_comp_domande.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === 5. Scatter plot: Coh vs Nat per domanda ===
plt.figure(figsize=(10,6))
for q in df["QuestionShort"].unique():
    subset = df[df["QuestionShort"] == q]
    plt.scatter(subset["Coh"], subset["Nat"], label=q, alpha=0.7, s=80)
plt.xlabel("Coerenza (Coh)")
plt.ylabel("Naturalness (Nat)")
plt.title("Correlazione Coh vs Nat per domanda")
plt.legend(title="Domande", bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.savefig(path + "correlazione_coh_nat_domande.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === Statistiche generali ===
stats = df[["Acc","Coh","Comp","Nat"]].agg(["mean","std","min","max"])
print(stats)

