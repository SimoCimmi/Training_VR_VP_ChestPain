import pandas as pd

import matplotlib.pyplot as plt

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

df.head()



import matplotlib.pyplot as plt

df.boxplot(column="Comp", by="AgeGroup", figsize=(8,6))
plt.title("Distribuzione della Completezza per Fascia di Età")
plt.suptitle("")  # rimuove titolo automatico
plt.ylabel("Completezza (Comp)")
plt.xlabel("Fascia di età")
plt.show()


import matplotlib.pyplot as plt

group_means = df.groupby("AgeGroup")[["Acc","Coh","Comp","Nat"]].mean()

group_means.plot(kind="bar", figsize=(10,6))
plt.ylabel("Punteggio medio")
plt.title("Punteggi medi per gruppo di età")
plt.xticks(rotation=0)
plt.show()

import numpy as np
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))
x_positions = {"Young":0, "Adult":1, "Senior":2}

for idx, row in df.iterrows():
    plt.scatter(
        x_positions[row["AgeGroup"]] + np.random.uniform(-0.1, 0.1),
        row["Comp"],
        s=80    )

plt.xticks([0,1,2], ["Young","Adult","Senior"])
plt.ylabel("Completezza (Comp)")
plt.title("Distribuzione dei valori di Completezza per gruppo di età")
plt.show()


'''
plt.figure(figsize=(10,6))
df[["Acc","Coh","Comp","Nat"]].boxplot()
plt.ylabel("Score")
plt.title("Distribuzione dei punteggi per metrica")
plt.show()


plt.figure(figsize=(12,6))
plt.bar(df["Patient"].astype(str), df["Comp"])
plt.xticks(rotation=90)
plt.ylabel("Completezza (Comp)")
plt.title("Punteggi di Completezza per Paziente")
plt.tight_layout()
plt.show()



group_age = df.groupby("AgeGroup")[["Acc","Coh","Comp","Nat"]].mean()

group_age.plot(kind="bar", figsize=(10,6))
plt.ylabel("Punteggio medio")
plt.title("Punteggio medio per metrica e gruppo di età")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()





stats = df[["Acc","Coh","Comp","Nat"]].agg(["mean","std","min","max"])
print(stats)

df_sorted = df.sort_values(by="Comp")
plt.figure(figsize=(12,6))
plt.bar(df_sorted["Patient"].astype(str), df_sorted["Comp"])
plt.xticks(rotation=90)
plt.ylabel("Completezza (Comp)")
plt.title("Completezza per paziente (ordinati dal più basso)")
plt.tight_layout()
plt.show()
'''