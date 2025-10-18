import os
import pandas as pd

# Visualizza tutte le colonne
pd.set_option('display.max_columns', None)

# Creazione path dinamico per leggere il file csv
base_dir = os.path.dirname(__file__)
path_origin_csv = os.path.join(base_dir, 'filteredDataset.csv')

# Lettura dataset
cds = pd.read_csv(path_origin_csv)
print(f"Numero di righe del dataset: {len(cds)}")

# -----------------------------
# CONVERSIONE DATI CATEGORICAL
# -----------------------------
cds["DIQ010"] = cds["DIQ010"].map({1:"Yes", 2:"No", 3:"Borderline"})
cds["WHQ070"] = cds["WHQ070"].map({1:"Yes", 2:"No"})
cds["RIDAGEYR"] = cds["RIDAGEYR"].map(lambda x: "From 80 and up" if x == 80 else x)
cds["RIAGENDR"] = cds["RIAGENDR"].map({1:"Male", 2:"Female"})
cds["RIDRETH1"] = cds["RIDRETH1"].map({
    1: "Mexican American",
    2: "Other Hispanic",
    3: "Non-Hispanic White",
    4: "Non-Hispanic Black",
    5: "Other/Multi-Racial"
})
cds["DMDEDUC2"] = cds["DMDEDUC2"].map({
    1: "Less than 9th grade",
    2: "9-11th grade / 12th grade with no diploma",
    3: "High school graduate / GED or equivalent",
    4: "Some college or AA degree",
    5: "College graduate or above"
})

# -----------------------------
# GESTIONE VALORI SPECIALI / MISSING
# -----------------------------
cds["DIQ010"] = cds["DIQ010"].replace(["7", "9", "."], pd.NA)
cds["DMDEDUC2"] = cds["DMDEDUC2"].replace([7, 9, "."], pd.NA)
cds["WHQ070"] = cds["WHQ070"].replace([7, 9, "."], pd.NA)
cds["PAD680"] = cds["PAD680"].replace([7777, 9999, "."], pd.NA)
cds["PAD800"] = cds["PAD800"].replace([7777, 9999, "."], pd.NA)
cds["PAD820"] = cds["PAD820"].replace([7777, 9999, "."], pd.NA)
cds["INDFMPIR"] = cds["INDFMPIR"].replace(["."], pd.NA)
cds["INDFMPIR"] = cds["INDFMPIR"].replace(5, "Value greater/equal to 5")

# Esami clinici e misure corporee
for col in ["LBXGLU", "LBXIN", "LBDHDD", "LBXTC", "BMXWT", "BMXHT", "BMXBMI"]:
    cds[col] = pd.to_numeric(cds[col], errors="coerce")  # '.' -> NaN

# Sostituzione 0 in Weight, Height, BMI con NaN
for col in ['BMXWT', 'BMXHT', 'BMXBMI']:
    cds[col] = cds[col].replace(0, pd.NA)


# -----------------------------
# CHECK valori mancanti
# -----------------------------
print("Numero di valori mancanti per colonna prima della pulizia:\n", cds.isna().sum())

# -----------------------------
# DATA CLEANING: 
# -----------------------------


# Rimozione righe con DIQ010 mancante (non deduciibile come positivo o negativo)
cds = cds.dropna(subset=["DIQ010"])

#Sostituzione mediana per PAD680, PAD800, PAD820
for col in ["PAD680", "PAD800", "PAD820"]:
    cds[col] = pd.to_numeric(cds[col], errors="coerce") # garantisce tipo numerico
    mediana = cds[col].median(skipna=True)
    cds[col] = cds[col].fillna(mediana)
    print(f"Sostituiti valori mancanti in {col} con la mediana: {mediana}")



# -----------------------------
# ANALISI PAD800 vs PAD820
# -----------------------------
countPAD800 = 0
countPAD820 = 0
for _, row in cds.iterrows():
    pad800 = row["PAD800"]
    pad820 = row["PAD820"]
    if pd.notna(pad800) and pd.notna(pad820):
        if pad800 > pad820:
            countPAD800 += 1
        else:
            countPAD820 += 1
print(f"Numero di righe con PAD800 > PAD820: {countPAD800} > {countPAD820}")

# -----------------------------
# RENAME COLUMNS
# -----------------------------
cds.rename(columns={
    "DIQ010": "Diabetes_diagnosis_positive",                    # Diagnosi di diabete positiva
    "LBXGLU": "Fasting_glucose",                                # Glucosio a digiuno
    "LBXIN": "Insulin_level",                                   # Livello di insulina
    "LBDHDD": "HDL_cholesterol",                                # Colesterolo HDL
    "LBXTC": "Total_cholesterol",                               # Colesterolo totale
    "BMXWT": "Weight_kg",                                       # Peso (kg)
    "BMXHT": "Height_cm",                                       # Altezza (cm)
    "BMXBMI": "BMI",                                            # Indice di massa corporea (BMI)
    "DR1TKCAL": "Total_calories_kcal",                          # Calorie totali (kcal)
    "DR1TPROT": "Protein_g",                                    # Proteine (g)
    "DR1TCARB": "Carbohydrates_g",                              # Carboidrati (g)
    "DR1TSUGR": "Total_sugars_g",                               # Zuccheri totali (g)
    "DR1TFIBE": "Dietary_fiber_g",                              # Fibre alimentari (g)
    "DR1TTFAT": "Total_fat_g",                                  # Grassi totali (g)
    "DR1TSFAT": "Saturated_fat_g",                              # Grassi saturi (g)
    "PAD680": "Daily_sedentary_minutes",                        # Minuti sedentari giornalieri
    "PAD800": "Moderate_activity_minutes",                      # Minuti di attività moderata
    "PAD820": "Vigorous_activity_minutes",                      # Minuti di attività intensa
    "WHQ070": "Tried_to_lose_weight_in_the_past_year",          # Ha cercato di perdere peso nell’ultimo anno
    "RIDAGEYR": "Age",                                          # Età
    "RIAGENDR": "Gender",                                       # Genere
    "RIDRETH1": "Ethnic_origin",                                # Origine etnica
    "DMDEDUC2": "Education_level",                              # Livello di istruzione
    "INDFMPIR": "Income_family_ratio_compared_to_the_poverty_line"  # Rapporto reddito familiare rispetto alla soglia di povertà
})


# -----------------------------
# Esportazione CSV pulito
# -----------------------------
path_destination_csv = os.path.join(base_dir, 'Clean_filteredDataset.csv')
cds.to_csv(path_destination_csv, index=False)

print("Dataset pulito esportato in Clean_filteredDataset.csv")
#print(cds.head(20))

# -----------------------------
# CHECK valori mancanti
# -----------------------------
print("Numero di valori mancanti per colonna dopo la pulizia:\n", cds.isna().sum())

print("Numero di righe con valori nulli: ", cds["DIQ010"].isna().sum())
righeNull = cds[cds["DIQ010"].isna()]
print(righeNull)
