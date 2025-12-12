import csv

input_file = "CSV_Valutazione_Umana_Risultati_domande_VP-gemma-3-27b-it_JUDGE-deepseek-r1-distill-qwen-32b.csv"
output_file = "CSV_Finale_Valutazione_Umana_Risultati_domande_VP-gemma-3-27b-it_JUDGE-deepseek-r1-distill-qwen-32b.csv"

# Legge il CSV e crea una nuova lista di righe con Explanation vuoto
rows = []
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        row["Explanation"] = ""   # <-- svuota il campo
        rows.append(row)

# Scrive il nuovo CSV con Explanation vuoto
with open(output_file, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Operazione completata: colonna 'Explanation' svuotata.")
