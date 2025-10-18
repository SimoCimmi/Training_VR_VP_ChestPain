import pandas as pd

# Leggi i due CSV
df1 = pd.read_csv("Clean_filteredDataset.csv")
df2 = pd.read_csv("COPIA_Clean_filteredDataset.csv")

# Controlla se hanno le stesse dimensioni
print("Clean_filteredDataset.csv df1:", df1.shape)
print("COPIA_Clean_filteredDataset.csv:", df2.shape)

# Controlla se sono esattamente uguali
if df1.equals(df2):
    print("I due CSV sono identici!")
else:
    print("I CSV differiscono.")

# Trova le differenze riga per riga
diff = df1.compare(df2)
print(diff)