import csv


csv_file = r"CSV_VALUTAZIONE_UMANA_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"
#csv_file = r"CSV_Risultati_domande_VP-openai_gpt-oss-20b_JUDGE-deepseek-r1-distill-qwen-32b.csv"
# Variabili per accumulare le somme
accuracy_sum = 0
coherence_sum = 0
completeness_sum = 0
naturalness_sum = 0
accuracyEvaluationHuman_sum = 0
coherenceEvaluationHuman_sum = 0
completenessEvaluationHuman_sum = 0
naturalnessEvaluationHuman_sum = 0

# Contatore dei valori
count = 0

# Lettura del CSV
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            # Somma delle metriche principali
            accuracy_sum += float(row.get('Accuracy', 0))
            coherence_sum += float(row.get('Coherence', 0))
            completeness_sum += float(row.get('Completeness', 0))
            naturalness_sum += float(row.get('Naturalness', 0))
            
            # Somma delle metriche umane, se presenti
            accuracyEvaluationHuman_sum += float(row.get('AccuracyEvaluationHuman', 0))
            coherenceEvaluationHuman_sum += float(row.get('CoherenceEvaluationHuman', 0))
            completenessEvaluationHuman_sum += float(row.get('CompletenessEvaluationHuman', 0))
            naturalnessEvaluationHuman_sum += float(row.get('NaturalnessEvaluationHuman', 0))

            # Stampa informazioni
            print(f"\n\nPatientID: {row.get('PatientID', 'N/A')}")
            print(f"Explanation: {row.get('Explanation', 'N/A')}")

            count += 1

        except (ValueError, TypeError):
            # Salta righe con valori mancanti o non numerici
            pass

# Calcolo medie
if count > 0:
    accuracy_avg = accuracy_sum / count
    coherence_avg = coherence_sum / count
    completeness_avg = completeness_sum / count
    naturalness_avg = naturalness_sum / count
    
    accuracyEvaluationHuman_avg = accuracyEvaluationHuman_sum / count
    coherenceEvaluationHuman_avg = coherenceEvaluationHuman_sum / count
    completenessEvaluationHuman_avg = completenessEvaluationHuman_sum / count
    naturalnessEvaluationHuman_avg = naturalnessEvaluationHuman_sum / count
    # Stampa risultati
    print(f"Numero di valori sommati: {count}")
    print(f"Media Accuracy: {accuracy_avg:.2f}")
    print(f"Media Coherence: {coherence_avg:.2f}")
    print(f"Media Completeness: {completeness_avg:.2f}")
    print(f"Media Naturalness: {naturalness_avg:.2f}")
    print(f"Media AccuracyEvaluationHuman: {accuracyEvaluationHuman_avg:.2f}")
    print(f"Media CoherenceEvaluationHuman: {coherenceEvaluationHuman_avg:.2f}")
    print(f"Media CompletenessEvaluationHuman: {completenessEvaluationHuman_avg:.2f}")
    print(f"Media NaturalnessEvaluationHuman: {naturalnessEvaluationHuman_avg:.2f}")
else:
    print("Nessun dato valido trovato.")
