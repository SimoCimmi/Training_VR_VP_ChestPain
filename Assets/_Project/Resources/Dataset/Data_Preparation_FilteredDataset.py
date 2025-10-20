import os
import pandas as pd
import numpy as np
import random

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


'''
Non utilizzata dato che mancano 2 valori su 3 in tutte le righe non consentento il suo utilizzo

Sostituisco i valori mancanti di di peso, altezza e BMI utilizzando le formule seguenti:
    
    altezza (m) = sqrt( peso (kg) / BMI )
    peso (kg) = altezza^2 * BMI
    BMI = peso (kg) / altezza^2 (m) 


for i, row in cds.iterrows():
    peso = row["BMXWT"]
    altezza = row["BMXHT"]
    bmi = row["BMXBMI"]

    altezza_m = altezza / 100 if pd.notna(altezza) else pd.NA  # Converti cm a m se non è NaN


    #Caso - Calcolo altezza se peso e BMI sono noti
    if(pd.isna(altezza) and pd.notna(peso) and pd.notna(bmi)):
        altezza_m = np.sqrt(peso/bmi)
        cds.ai[i, "BMXHT"] = altezza_m * 100  # Converti m a cm
    
    #Caso - Calcolo peso se altezza e BMI sono noti
    if(pd.isna(peso) and pd.notna(altezza_m) and pd.notna(bmi)):
        cds.ai[i, "BMXWT"] = bmi * (altezza_m ** 2)

    #Caso - Calcolo BMI se peso e altezza sono noti
    if(pd.isna(bmi) and pd.notna(peso) and pd.notna(altezza_m)):
        cds.ai[i, "BMXBMI"] = peso / (altezza_m ** 2)
    

print("\nDopo la stima dei valori mancanti di peso, altezza e BMI:")
mask = cds[["BMXWT", "BMXHT", "BMXBMI"]].isna().any(axis=1) #per ogni riga (axis=1) valuta se almeno una colonna tra le tre è True (ovvero NaN).
righe_null = cds.loc[mask, ["SEQN", "BMXWT", "BMXHT", "BMXBMI"]]
print(righe_null)
count_null = (cds[["BMXWT", "BMXHT", "BMXBMI"]].isna().sum(axis=1) >= 2).sum()
print("Numero di righe con almeno 2 valore mancante:", count_null)

'''

# -----------------------------
# IMPUTAZIONE BMI, PESO E ALTEZZA 
# -----------------------------

# Converti altezza in metri per i calcoli
cds["BMXHT_m"] = cds["BMXHT"] / 100.0

# Salva valori originali e crea flag per imputazioni
for col in ["BMXWT", "BMXHT", "BMXBMI"]:
    cds[f"{col}_original"] = cds[col]      # valore originale
    cds[f"{col}_imputed"] = False          # flag se imputato

# Funzione per stampare le imputazioni
def print_imputation(seqn, col, old, new):
    print(f"Riga SEQN={seqn} | {col} imputato: {old} -> {new}")

# -----------------------------
# Imputaazioni sfruttando la seguente formula e le sue derivate sostituisco i valori mancanti di di peso, altezza e BMI::
#    altezza (m) = sqrt( peso (kg) / BMI )
#    peso (kg) = altezza^2 * BMI
#    BMI = peso (kg) / altezza^2 (m) 


# -----------------------------
# Step 1: Imputazione BMI quando mancante ma peso e altezza presenti
# Formula: BMI = peso (kg) / altezza^2 (m)
# Condizione: BMI mancante, ma peso e altezza disponibili
mask_bmi_missing = cds["BMXBMI"].isna() & cds["BMXWT"].notna() & cds["BMXHT_m"].notna()
for idx in cds[mask_bmi_missing].index:
    old = cds.at[idx, "BMXBMI"]  # valore originale (NaN)
    # Calcolo BMI usando peso e altezza
    new = round(cds.at[idx, "BMXWT"] / (cds.at[idx, "BMXHT_m"] ** 2), 2)
    cds.at[idx, "BMXBMI"] = new             # aggiorna BMI
    cds.at[idx, "BMXBMI_imputed"] = True    # segna come imputato
    print_imputation(cds.at[idx, "SEQN"], "BMXBMI", old, new)

# -----------------------------
# Step 2: Imputazione peso quando mancante ma altezza e BMI presenti
# Formula: peso (kg) = altezza^2 (m) * BMI
# Condizione: peso mancante, ma altezza e BMI disponibili
mask_wt_missing = cds["BMXWT"].isna() & cds["BMXBMI"].notna() & cds["BMXHT_m"].notna()
for idx in cds[mask_wt_missing].index:
    old = cds.at[idx, "BMXWT"]  # valore originale (NaN)
    # Calcolo peso usando altezza e BMI
    new = round(cds.at[idx, "BMXBMI"] * (cds.at[idx, "BMXHT_m"] ** 2),2)
    cds.at[idx, "BMXWT"] = new             # aggiorna peso
    cds.at[idx, "BMXWT_imputed"] = True    # segna come imputato
    print_imputation(cds.at[idx, "SEQN"], "BMXWT", old, new)

# -----------------------------
# Step 3: Imputazione altezza quando mancante ma peso e BMI presenti
# Formula: altezza (m) = sqrt( peso (kg) / BMI )
# Condizione: altezza mancante, ma peso e BMI disponibili
mask_ht_missing = cds["BMXHT"].isna() & cds["BMXBMI"].notna() & cds["BMXWT"].notna()
for idx in cds[mask_ht_missing].index:
    old = cds.at[idx, "BMXHT"]  # valore originale (NaN)
    # Calcolo altezza in metri
    new_m = round((cds.at[idx, "BMXWT"] / cds.at[idx, "BMXBMI"]) ** 0.5, 2)
    new_cm = new_m * 100        # converti in cm
    cds.at[idx, "BMXHT_m"] = new_m       # salva altezza in metri temporanea
    cds.at[idx, "BMXHT"] = new_cm        # aggiorna altezza in cm
    cds.at[idx, "BMXHT_imputed"] = True  # segna come imputato
    print_imputation(cds.at[idx, "SEQN"], "BMXHT", old, new_cm)

    print_imputation(cds.at[idx, "SEQN"], "BMXHT", old, new_cm)

# -----------------------------
# Step 4: Imputazione stratificata per età e genere
# -----------------------------
cds["Age_group"] = pd.cut(
    cds["RIDAGEYR"].astype(float),
    bins=[0,18,30,45,60,75,1000],
    labels=["<18","18-29","30-44","45-59","60-74","75+"],
    right=False
)

def stratified_fillna(df, col, group_cols):
    """Riempi NaN con mediana stratificata e stampa imputazioni."""
    # Risolvo il FutureWarning impostando observed=True
    median_series = df.groupby(group_cols, observed=True)[col].median()

    for idx, row in df[df[col].isna()].iterrows():
        key = tuple(row[g] for g in group_cols)
        if key in median_series.index:
            old = df.at[idx, col]
            new_val = round(median_series.loc[key], 2)
            df.at[idx, col] = new_val
            print(f"Riga SEQN={row['SEQN']} | {col} imputato con mediana stratificata: {new_val}")
    return df

group_cols = ["Age_group", "RIAGENDR"]
for col in ["BMXWT", "BMXHT", "BMXBMI"]:
    cds = stratified_fillna(cds, col, group_cols)

# -----------------------------
# Step 5: Fallback mediana globale se ancora NaN
# -----------------------------
for col in ["BMXWT", "BMXHT", "BMXBMI"]:
    mask_global = cds[col].isna()
    median_global = round(cds[col].median(skipna=True), 2)
    for idx in cds[mask_global].index:
        old = cds.at[idx, col]
        cds.at[idx, col] = median_global
        print(f"Riga SEQN={cds.at[idx,'SEQN']} | {col} imputato con mediana globale: {median_global}")

# -----------------------------
# Pulizia finale: rimuovo colonne temporanee
# -----------------------------
cds.drop(columns=[
    "BMXHT_m",
    "BMXWT_original", "BMXWT_imputed",
    "BMXHT_original", "BMXHT_imputed",
    "BMXBMI_original", "BMXBMI_imputed",
    "Age_group"
], inplace=True)


# -----------------------------
# IMPUTAZIONE WHQ070 ovvero Ha cercato di perdere peso nell’ultimo anno (Tried_to_lose_weight_in_the_past_year)
# -----------------------------
#Si utilizza la BMI per dedurre se una persona ha cercato di perdere peso nell'ultimo anno, con probabilità più alta se la BMI è elevata.
def impute_try_to_lose(row):
    if(pd.isna(row["WHQ070"])):
        bmi = row["BMXBMI"]
        if pd.notna(bmi):
            if bmi > 25:
                # 80% di probabilità di aver provato a perdere peso
                return "Yes" if random.random() < 0.8 else "No"
            else:
                # 30% di probabilità di aver provato a perdere peso
                return "Yes" if random.random() < 0.3 else "No"
        else:
            # Se BMI mancante, assegna casualmente (Precedentemente la BMI è stata imputata, quindi questo caso non si dovrebbe verificare)
            return random.choice(["Yes", "No"])
    else:
        return row["WHQ070"]
    
# Applica la funzione al dataframe
cds["WHQ070"] = cds.apply(impute_try_to_lose, axis=1)


print("Numero di valori WHQ070 null:", cds["WHQ070"].isna().sum())


# -----------------------------
# IMPUTAZIONE DMDEDUC2 ovvero Education_level (Education_level )
# -----------------------------
imputazioniGruppo = 0
imputazioniGlobali = 0

def impute_education_age_gender(row):
    global imputazioniGruppo,   imputazioniGlobali
    
    if pd.isna(row["DMDEDUC2"]):
        group = cds[
            (cds["Age_group"] == row["Age_group"]) &
            (cds["RIAGENDR"] == row["RIAGENDR"]) 
        ]["DMDEDUC2"].dropna()

        print(f"Riga SEQN={row['SEQN']}")
        print(f"Age_group={row['Age_group']}, Gender={row['RIAGENDR']}")
        print(f"Numero valori disponibili nel gruppo per l'imputazione: {len(group)}")

        if len(group) > 0:
            chosen_value = np.random.choice(group.values)
            print(f"Imputazione scelta dal gruppo: {chosen_value}")
            imputazioniGruppo += 1
            return chosen_value
        else:
            # Fallback: scegli random da tutto il dataset
            chosen_value_global = np.random.choice(cds["DMDEDUC2"].dropna().values)
            print(f"Imputazione scelta globalmente: {chosen_value_global}")
            imputazioniGlobali += 1
            return chosen_value_global
    else:
        return row["DMDEDUC2"]
    
cds["Age_group"] = pd.cut(
        cds["RIDAGEYR"].astype(float),
        bins=[0,18,30,45,60,75,1000],
        labels=["<18","18-29","30-44","45-59","60-74","75+"],
        right=False
    )  
cds["DMDEDUC2"] = cds.apply(impute_education_age_gender, axis=1)
cds.drop(columns=["Age_group"], inplace=True)

# Stampa contatori
print(f"DMDEDUC2(Education_level)- Numero imputazioni dal gruppo stratificato: {imputazioniGruppo}")
print(f"DMDEDUC2(Education_level) - Numero imputazioni globali: {imputazioniGlobali}")
# -----------------------------
# CONVERSIONE DATI CATEGORICAL
# -----------------------------

cds["RIDAGEYR"] = cds["RIDAGEYR"].map(lambda x: "From 80 and up" if x == 80 else x)

# -----------------------------
# RENAME COLUMNS
# -----------------------------
cds.rename(columns={
    "DIQ010": "Diabetes_diagnosis_positive",                    # Diagnosi di diabete positiva
    "LBXGLU": "Fasting_glucose",                                # Glucosio a digiuno
    "LBXIN": "Insulin_level",                                   # Livello di insulina
    "BMXWT": "Weight_kg",                                       # Peso (kg)
    "BMXHT": "Height_cm",                                       # Altezza (cm)
    "BMXBMI": "BMI",                                            # Indice di massa corporea (BMI)
    "LBDHDD": "HDL_cholesterol",                                # Colesterolo HDL
    "LBXTC": "Total_cholesterol",                               # Colesterolo totale
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
}, inplace=True)


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
print("Numero di righe del dataset pulito: ", len(cds))


print(cds.head(5))
