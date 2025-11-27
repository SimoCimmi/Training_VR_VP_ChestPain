import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import os

# === Percorso dove salvare i PDF ===
path = r"C:\Users\vince\Documents\Vincenzo Medica\UNISA Google Drive\Tesi\SchemiTesi\GraficiValutazioneLLM\\"

# Crea la cartella se non esiste
os.makedirs(path, exist_ok=True)


data = [
    [135140, "Male", "Young", "Yes", 4.25, 4.75, 4.00, 5.00],
    [136641, "Male", "Young", "No", 4.75, 4.75, 3.75, 4.75],
    [132602, "Male", "Young", "Borderline", 4.50, 4.75, 4.50, 5.00],
    [137037, "Male", "Adult", "Yes", 4.50, 4.50, 4.00, 4.50],
    [137870, "Male", "Adult", "No", 4.75, 4.75, 4.75, 5.00],
    [131546, "Male", "Adult", "Borderline", 4.25, 4.50, 3.75, 5.00],
    [136691, "Male", "Senior", "Yes", 4.75, 4.75, 4.25, 5.00],
    [138563, "Male", "Senior", "No", 4.75, 4.75, 4.00, 5.00],
    [137112, "Female", "Young", "Yes", 4.50, 4.75, 4.50, 4.75],
    [137856, "Female", "Young", "No", 4.75, 4.50, 4.00, 4.50],
    [136670, "Female", "Young", "Borderline", 4.75, 4.75, 4.00, 5.00],
    [138374, "Female", "Adult", "Yes", 4.25, 4.50, 3.75, 5.00],
    [139172, "Female", "Adult", "No", 4.50, 5.00, 4.00, 5.00],
    [133751, "Female", "Adult", "Borderline", 4.50, 4.75, 4.25, 5.00],
    [138162, "Female", "Senior", "Yes", 4.25, 5.00, 4.25, 4.50],
    [137302, "Female", "Senior", "No", 4.25, 4.75, 4.50, 4.75]
]

df = pd.DataFrame(data, columns=["Patient","Gender","AgeGroup","Diagnosis","Acc","Coh","Comp","Nat"])


# === GRAFICO 1: Boxplot Completezza per Fascia Età ===
plt.figure(figsize=(8,6))
df.boxplot(column="Comp", by="AgeGroup")
plt.title("Distribuzione della Completezza per Fascia di Età")
plt.suptitle("")
plt.ylabel("Comp")
plt.xlabel("Fascia di età")

plt.savefig(path + "boxplot_completezza_per_eta.pdf", format="pdf", bbox_inches="tight")
plt.close()


'''
# === GRAFICO 3: Scatter Completezza ===
plt.figure(figsize=(8,6))
x_positions = {"Young":0, "Adult":1, "Senior":2}

for _, row in df.iterrows():
    plt.scatter(
        x_positions[row["AgeGroup"]] + np.random.uniform(-0.1, 0.1),
        row["Comp"],
        s=80
    )

plt.xticks([0,1,2], ["Young","Adult","Senior"])
plt.ylabel("Comp")
plt.title("Distribuzione dei valori di Completezza per gruppo di età")

plt.savefig(path + "scatter_completezza_eta.pdf", format="pdf", bbox_inches="tight")
plt.close()

'''

# === GRAFICO 4: Boxplot metriche ===
plt.figure(figsize=(10,6))
# Il boxplot mostra la distribuzione di ciascuna metrica (mediana, quartili,
# valori min/max ed eventuali outlier).
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

# Aggiungere i valori sulle barre
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

# Aggiungere i valori sulle barre
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

# Calcolo media delle metriche per Gender
group_gender = df.groupby("Gender")[["Acc", "Coh", "Comp", "Nat"]].mean()

plt.figure(figsize=(10,6))

# Plot multi-barre (ogni metrica ha 2 barre: Male e Female)
ax = group_gender.plot(kind="bar", figsize=(10,6))

plt.title("Metriche medie per Genere")
plt.ylabel("Punteggio medio")
plt.xlabel("Genere")
plt.xticks(rotation=0)

# Aggiungere valori su ogni barra
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2)

plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()

plt.savefig(path + "metriche_per_genere.pdf", format="pdf", bbox_inches="tight")
plt.close()


# === GRAFICO: Metriche per Diagnosi (tutte le metriche nello stesso grafico) ===
# === ORDINAMENTO PERSONALIZZATO DIAGNOSIS ===
order = ["Yes", "No", "Borderline"]

df["Diagnosis"] = pd.Categorical(df["Diagnosis"], categories=order, ordered=True)

# Ricalcolo media con ordine imposto
group_diag = df.groupby("Diagnosis")[["Acc", "Coh", "Comp", "Nat"]].mean()

plt.figure(figsize=(10,6))
ax = group_diag.plot(kind="bar", figsize=(10,6))

plt.title("Metriche medie per Diagnosi")
plt.ylabel("Punteggio medio")
plt.xlabel("Diagnosi")
plt.xticks(rotation=0)

# Aggiungere valori sulle barre
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=2)

plt.legend(title="Metriche", bbox_to_anchor=(1.05,1), loc="upper left")
plt.tight_layout()
plt.savefig(path + "metriche_per_diagnosi.pdf", format="pdf", bbox_inches="tight")
plt.close()

# === Statistiche ===
stats = df[["Acc","Coh","Comp","Nat"]].agg(["mean","std","min","max"])
print(stats)


