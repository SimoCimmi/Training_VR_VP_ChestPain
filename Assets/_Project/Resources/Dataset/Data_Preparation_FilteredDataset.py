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
cds["DIQ010"].replace(["7", "9", "."], pd.NA, inplace=True)
cds["DMDEDUC2"].replace([7, 9, "."], pd.NA, inplace=True)
cds["WHQ070"].replace([7, 9, "."], pd.NA, inplace=True)
cds["PAD680"].replace([7777, 9999, "."], pd.NA, inplace=True)
cds["PAD800"].replace([7777, 9999, "."], pd.NA, inplace=True)
cds["PAD820"].replace([7777, 9999, "."], pd.NA, inplace=True)
cds["INDFMPIR"].replace(["."], pd.NA, inplace=True)
cds["INDFMPIR"].replace(5, "Value greater/equal to 5", inplace=True)

# Esami clinici e misure corporee
for col in ["LBXGLU", "LBXIN", "LBDHDD", "LBXTC", "BMXWT", "BMXHT", "BMXBMI"]:
    cds[col] = pd.to_numeric(cds[col], errors="coerce")  # '.' -> NaN

# Sostituzione 0 in Weight, Height, BMI con NaN
for col in ['BMXWT', 'BMXHT', 'BMXBMI']:
    cds[col].replace(0, pd.NA, inplace=True)

# -----------------------------
# DATA CLEANING: Sostituzione mediana per attività fisica
# -----------------------------
for col in ["PAD680", "PAD800", "PAD820"]:
    mediana = cds[col].median(skipna=True)
    cds[col].fillna(mediana, inplace=True)
    print(f"Sostituiti valori mancanti in {col} con la mediana: {mediana}")

# -----------------------------
# CHECK valori mancanti
# -----------------------------
print("Numero di valori mancanti per colonna dopo la pulizia:\n", cds.isna().sum())

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
    "DIQ010": "Diabetes_diagnosis_positive",
    "LBXGLU": "Fasting_glucose",
    "LBXIN": "Insulin_level",
    "LBDHDD": "HDL_cholesterol",
    "LBXTC": "Total_cholesterol",
    "BMXWT": "Weight_kg",
    "BMXHT": "Height_cm",
    "BMXBMI": "BMI",
    "DR1TKCAL": "Total_calories_kcal",
    "DR1TPROT": "Protein_g",
    "DR1TCARB": "Carbohydrates_g",
    "DR1TSUGR": "Total_sugars_g",
    "DR1TFIBE": "Dietary_fiber_g",
    "DR1TTFAT": "Total_fat_g",
    "DR1TSFAT": "Saturated_fat_g",
    "PAD680": "Daily_sedentary_minutes",
    "PAD800": "Moderate_activity_minutes",
    "PAD820": "Vigorous_activity_minutes",
    "WHQ070": "Tried_to_lose_weight_in_the_past_year",
    "RIDAGEYR": "Age",
    "RIAGENDR": "Gender",
    "RIDRETH1": "Ethnic_origin",
    "DMDEDUC2": "Education_level",
    "INDFMPIR": "Income_family_ratio_compared_to_the_poverty_line"
}, inplace=True)

# -----------------------------
# Esportazione CSV pulito
# -----------------------------
path_destination_csv = os.path.join(base_dir, 'Clean_filteredDataset.csv')
cds.to_csv(path_destination_csv, index=False)

print("Dataset pulito esportato in Clean_filteredDataset.csv")
print(cds.head(20))
