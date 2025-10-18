
#Esecuzione:
#1. Aprire cmd
#2. Posizionarsi nella cartella in cui si trova Data_Preparation_FilteredDataset.py
#3. Lanciare: python Data_Preparation_FilteredDataset.py
import os
import pandas as pd

#Usiamo un dataset strutturato

pd.set_option('display.max_columns', None)  
#None significa nessun limite sul numero di colonne mostrate.
# Mostra tutte le colonne

#Creazione path dinamico per leggere il file csv
base_dir = os.path.dirname(__file__)
path_origin_cvs = os.path.join(base_dir, 'filteredDataset.csv')

df = pd.read_csv(path_origin_cvs)
print(f"Numero di righe del datset: {len(df)}")


cds = pd.read_csv(path_origin_cvs)

#print(ds["WHQ070"].head(5))

#print(cds["RIDAGEYR"].to_string())


#CONVERSIONE DEI DATI IN FORMATO PIU' SEMPLICE DA LEGGERE

cds["DIQ010"] = cds["DIQ010"].map({1:"Yes", 2:"No", 3:"Borderline"}).astype(str)  #DIQ010 – Diagnosi di diabete dal medico:
#LBXGLU – Glucosio a digiuno (mg/dL):
#LBXIN – Livello di insulina:
#LBDHDD – Colesterolo HDL ("buono")


cds["WHQ070"] = cds["WHQ070"].map({1:"Yes", 2: "No"}).astype(str)  #WHQ070 – Ha provato a perdere peso nell’ultimo anno:

#Se il valore della colonna è 80, sostituiscilo con la stringa "Dagli 80 in su" (From 80 and up) altrimenti lascia il valore che trovi.
cds["RIDAGEYR"] = cds["RIDAGEYR"].map(lambda x: "From 80 and up" if x == 80 else x).astype(str) #RIDAGEYR – Eta' (anni)


cds["RIAGENDR"] = cds["RIAGENDR"].map({1:"Male", 2:"Female"}).astype(str) #RIAGENDR – Genere (Male = Maschio, Female = Femmina)


cds["RIDRETH1"] = cds["RIDRETH1"].map({
    1: "Mexican American",
    2: "Other Hispanic",
    3: "Non-Hispanic White",
    4: "Non-Hispanic Black",
    5: "Other/Multi-Racial"
}).astype(str)  # Origine etnica
''' 
    1:Messicano-Americano",
    2: "Altro ispanico",
    3: "Bianco non ispanico",
    4: "Nero non ispanico",
    5: "Altro/Multirazziale"
'''

cds["DMDEDUC2"] = cds["DMDEDUC2"].map({
    1: "Less than 9th grade",
    2: "9-11th grade / 12th grade with no diploma",
    3: "High school graduate / GED or equivalent",
    4: "Some college or AA degree",
    5: "College graduate or above"
}).astype(str)  # Livello di istruzione (solo adulti 20+)

# I valori 7, 9 e . erano indicati come missing, quindi li gestiamo settandoli a pd.NA (valore nullo)
cds["DMDEDUC2"] = cds["DMDEDUC2"].replace(["7", "9", "."], pd.NA)
cds["WHQ070"] = cds["WHQ070"].replace(["7", "9", "."], pd.NA)
cds["PAD680"] = cds["PAD680"].replace([7777, 9999, "."], pd.NA)
cds["PAD800"] = cds["PAD800"].replace([7777, 9999, "."], pd.NA)
cds["PAD820"] = cds["PAD820"].replace([7777, 9999, "."], pd.NA)
cds["INDFMPIR"] = cds["INDFMPIR"].replace(["."], pd.NA)

# Attivita' fisica: non categoriali ma gestiamo i missing gia' sopra

# Rapporto reddito/famiglia
# I valori numerici rimangono, ma possiamo sostituire 5 con un’etichetta testuale, lo sostituiamo con Value greater/equal to 5 (Valore maggiore o uguale a 5)
cds["INDFMPIR"] = cds["INDFMPIR"].map({5: "Value greater/equal to 5"}).astype(str)  # Rapporto reddito/famiglia rispetto soglia poverta'


#################
# DATA CLEANING #
#################

# GESTIONE MISSING / VALORI SPECIALI

cds["DIQ010"] = cds["DIQ010"].replace(["7", "9", "."], pd.NA)
'''
Seleziona la colonna DIQ010 e tramite il metodo replace() sostituisce i valori:
- "7" valore speciale che indica dati mancanti o non applicabili nel dataset NHANES
- "9"  un altro codice per dati mancanti
- "."  spesso usato per rappresentare missing value nei dataset esportati da software statistici
Tutti questi valori vengono sostituiti con pd.NA, che è il tipo di Pandas per i missing values (equivalente a NaN).
'''
# Storia del peso e istruzione
cds["DMDEDUC2"] = cds["DMDEDUC2"].replace([7, 9, "."], pd.NA)
cds["WHQ070"] = cds["WHQ070"].replace([7, 9, "."], pd.NA)

# Attivita' fisica
cds["PAD680"] = cds["PAD680"].replace([7777, 9999, "."], pd.NA)
cds["PAD800"] = cds["PAD800"].replace([7777, 9999, "."], pd.NA)
cds["PAD820"] = cds["PAD820"].replace([7777, 9999, "."], pd.NA)

# Rapporto reddito/famiglia
cds["INDFMPIR"] = cds["INDFMPIR"].replace(["."], pd.NA)

# Esami clinici e misure corporee: valori out-of-range o '.' -> missing
#pd.to_numeric() prova a convertire i valori in numeri (int o float).
#errors="coerce" dice a Pandas: Se un valore non può essere convertito in numero (es. "." o stringhe non numeriche), sostituiscilo con NaN.
for col in ["LBXGLU", "LBXIN", "LBDHDD", "LBXTC", "BMXWT", "BMXHT", "BMXBMI"]:
    cds[col] = pd.to_numeric(cds[col], errors="coerce")  # converte '.' in NaN



#Gestione valori mancanti:

print("Numero di valori mancanti per colonna prima della pulizia :\n ", cds.isna().sum() )
cds.isna()


# PAD680 – Daily sedentary minutes (Minuti sedentari giornalieri)
# PAD800 – Moderate activity minutes (Minuti di attività moderata)
# PAD820 – Vigorous activity minutes (Minuti di attività vigorosa)

countPAD800 = 0
countPAD820 = 0
for index, row in cds.iterrows():
    pad800 = row["PAD800"]
    pad820 = row["PAD820"]
    if(pd.notna(pad800) and pd.notna(pad820)):
        if (row["PAD800"] > row["PAD820"]):
            countPAD800 += 1
        else:
            countPAD820 += 1
    #Ci dice che i Minuti di attività moderata (PAD800) sono maggiori dei Minuti di attività vigorosa (PAD820).
print(f"Numero di righe con PAD800 > PAD820: {countPAD800} > {countPAD820}")

'''for index, row in cds.iterrows():
    if pd.isna(row["PAD820"]):
        print(f"Tupla con PAD820 mancante (riga {index}):")
        print(row.to_dict())'''


for col in ["PAD680"]:
    mediana = cds[col].median(skipna=True)  # Calcola la mediana ignorando i valori NaN
print(f"Mediana di PAD680: {mediana}")

for col in ["PAD680"]:
    if(cds[col].isna().any()): #.any() restituisce True se almeno un valore è NaN
        cds[col] = mediana  # Sostituisce i valori NaN con la mediana calcolata
        print(f"Sostituiti valori mancanti in {col} con la mediana: {mediana}")



for col in ["PAD800"]:
    mediana = cds[col].median(skipna=True)  # Calcola la mediana ignorando i valori NaN
print(f"Mediana di PAD800: {mediana}")

for col in ["PAD800"]:
    if(cds[col].isna().any()): #.any() restituisce True se almeno un valore è NaN
        cds[col] = mediana  # Sostituisce i valori NaN con la mediana calcolata
        print(f"Sostituiti valori mancanti in {col} con la mediana: {mediana}")    



for col in ["PAD820"]:
    mediana = cds[col].median(skipna=True)  # Calcola la mediana ignorando i valori NaN
print(f"Mediana di {col}: {mediana}")

        
for col in ["PAD820"]:
    if(cds[col].isna().any()): #.any() restituisce True se almeno un valore è NaN
        cds[col] = mediana  # Sostituisce i valori NaN con la mediana calcolata
        print(f"Sostituiti valori mancanti in {col} con la mediana: {mediana}")   


'''for col in ["PAD680"]:
    media = cds[col].mean(skipna=True)  # Calcola la media ignorando i valori NaN
print(f"Media di {col}: {media}")   
#Scarta la media perchè influenzata dai valori estremi (outlier)
'''

        
print("Numero di valori mancanti per colonna dopo la pulizia :\n ", cds.isna().sum() )
cds.isna()

'''
    if(row["PAD820"] is pd.NA):
        print(cds.loc[index]) 
    
    if row["PAD800"] is pd.NA and row["PAD820"] is pd.NA:
            print(f"Relazione tra valori mancanti in PAD680 e PAD800 o PAD820 - Riga {index}")    



    if row["PAD680"] is pd.NA:
        print(f"Valori mancanti - Riga {index}, Colonna {col}")
    if row["PAD800"] is pd.NA:
        print(f"--Valori mancanti - Riga {index}, Colonna {col}")
    if row["PAD820"] is pd.NA:
        print(f"++++Valori mancanti - Riga {index}, Colonna {col}")
'''




'''
print(f"PAD800:")
for value in cds["PAD800"]:
    print(value)
'''






# RENAME COLUMNS
cds = cds.rename(columns={

    # Diabetes
    "DIQ010": "Diabetes_diagnosis_positive",                # DIQ010 – Diabetes diagnosis positive (Diagnosi di diabete positiva)

    # Clinical exams
    "LBXGLU": "Fasting_glucose",                            # LBXGLU – Fasting glucose (Glucosio a digiuno)
    "LBXIN": "Insulin_level",                               # LBXIN – Insulin level (Livello di insulina)
    "LBDHDD": "HDL_cholesterol",                            # LBDHDD – HDL cholesterol (Colesterolo HDL)
    "LBXTC": "Total_cholesterol",                           # LBXTC – Total cholesterol (Colesterolo totale)

    # Body measurements
    "BMXWT": "Weight_kg",                                   # BMXWT – Weight (kg) (Peso in kg)
    "BMXHT": "Height_cm",                                   # BMXHT – Height (cm) (Altezza in cm)
    "BMXBMI": "BMI",                                        # BMXBMI – Body Mass Index (Indice di massa corporea - BMI)

    # Diet
    "DR1TKCAL": "Total_calories_kcal",                      # DR1TKCAL – Total calories (Calorie totali in kcal)
    "DR1TPROT": "Protein_g",                                # DR1TPROT – Protein (g) (Proteine in grammi)
    "DR1TCARB": "Carbohydrates_g",                          # DR1TCARB – Carbohydrates (g) (Carboidrati in grammi)
    "DR1TSUGR": "Total_sugars_g",                           # DR1TSUGR – Total sugars (g) (Zuccheri totali in grammi)
    "DR1TFIBE": "Dietary_fiber_g",                          # DR1TFIBE – Dietary fiber (g) (Fibre alimentari in grammi)
    "DR1TTFAT": "Total_fat_g",                              # DR1TTFAT – Total fat (g) (Grassi totali in grammi)
    "DR1TSFAT": "Saturated_fat_g",                          # DR1TSFAT – Saturated fat (g) (Grassi saturi in grammi)

    # Physical activity
    "PAD680": "Daily_sedentary_minutes",                    # PAD680 – Daily sedentary minutes (Minuti sedentari giornalieri)
    "PAD800": "Moderate_activity_minutes",                  # PAD800 – Moderate activity minutes (Minuti di attività moderata)
    "PAD820": "Vigorous_activity_minutes",                  # PAD820 – Vigorous activity minutes (Minuti di attività vigorosa)

    # Weight history
    "WHQ070": "Tried_to_lose_weight_in_the_past_year",      # WHQ070 – Tried to lose weight in the past year (Ha provato a perdere peso nell’ultimo anno)   

    # Demographics
    "RIDAGEYR": "Age",                                      # RIDAGEYR – Age (Età in anni)
    "RIAGENDR": "Gender",                                   # RIAGENDR – Gender (Genere)
    "RIDRETH1": "Ethnic_origin",                            # RIDRETH1 – Ethnic origin (Origine etnica)
    "DMDEDUC2": "Education_level",                          # DMDEDUC2 – Education level (Livello di istruzione - solo adulti 20+)
    "INDFMPIR": "Income_family_ratio_compared_to_the_poverty_line",           # INDFMPIR – Income/family ratio compared to the poverty line (Rapporto reddito/famiglia rispetto alla soglia di povertà)
})


#print(cds.head(5)) #Mostra le prime 5 righe del DataFrame cds dopo le modifiche.

#print(df.read_csv(r"C:\Training_VR_VP\Assets\_Project\Resources\Dataset\filteredDataset.csv"))


#Esportazione del dataset pulito:
path_destination_csv = os.path.join(base_dir, 'Clean_filteredDataset.csv')
cds.to_csv(path_destination_csv, index=False) 
#Ogni DataFrame ha un indice (numeri da 0 a N-1 per le righe).
# Se non metti index=False, il CSV salverebbe anche questa colonna “extra” con i numeri delle righe.

#NOTE: Quando si esegue non bisogna avere il file Clean_filteredDataset.csv aperto.
