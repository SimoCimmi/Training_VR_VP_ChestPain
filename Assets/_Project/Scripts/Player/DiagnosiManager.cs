using UnityEngine;
using TMPro;
using System.Collections.Generic;

public class DiagnosiManager : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private TMP_Text feedbackText;   // +1 / -1 con emoji
    [SerializeField] private TMP_Text anchorText;     // spiegazione Anchor
    [SerializeField] private TMP_Text punteggioText;  // punteggio totale
    [SerializeField] private TMP_Text diagnosiText;   // diagnosi eseguite

    private int punteggio = 0;          // punteggio cumulativo
    private int diagnosiEseguite = 0;   // counter diagnosi
    private CartellaClinica pazienteCorrente;
    private bool diagnosiGiaFatta = false;

    // ──────────────────────────────────────────────────────────────
    // Chiamato dallo SpawnPaziente subito dopo lo spawn del modello
    public void SetPazienteCorrente(CartellaClinica p)
    {
        pazienteCorrente = p;

        // reset UI di feedback (non del punteggio!)
        feedbackText.gameObject.SetActive(false);
        anchorText.gameObject.SetActive(false);
        diagnosiGiaFatta = false;
    }

    // ──────────────────────────────────────────────────────────────
    // Collegare ai bottoni (1 = Diabete, 2 = Non Diabete, 3 = Borderline)
    public void ControllaDiagnosi(int sceltaUtente)
    {
        if (diagnosiGiaFatta) return;
        if (pazienteCorrente == null)
        {
            Debug.LogWarning("[DiagnosiManager] Nessun paziente impostato!");
            return;
        }
        bool corretta;
        switch (sceltaUtente)
        {
            case 1:
                corretta = pazienteCorrente.DIQ010 == "Yes";
                break;
            case 2:
                corretta = pazienteCorrente.DIQ010 == "No";
                break;
            case 3:
                corretta = pazienteCorrente.DIQ010 == "Borderline";
                break;
            default:
                corretta = false;
            break;

        }


        punteggio += corretta ? 1 : -1;
        diagnosiEseguite += 1;

        AggiornaPunteggioUI();
        MostraFeedback(corretta ? "+1" : "-1");
        MostraAnchorExplanation(corretta);
        diagnosiGiaFatta = true;
    }

    // ──────────────────────────────────────────────────────────────
    // UI: pannello punteggio & diagnosi
    private void AggiornaPunteggioUI()
    {
        punteggioText.text = $"Punteggio: {punteggio}";
        diagnosiText.text = $"Diagnosi eseguite: {diagnosiEseguite}";
    }

    // ──────────────────────────────────────────────────────────────
    // Feedback immediato (+1/-1 con emoji)
    private void MostraFeedback(string msg)
    {
        bool isPlus = msg == "+1";

        feedbackText.text = isPlus
            ? "✔️ Diagnosi corretta (+1)"
            : "❌ Diagnosi errata (-1)";
        feedbackText.color = isPlus ? Color.green : Color.red;

        feedbackText.gameObject.SetActive(true);

        CancelInvoke(nameof(NascondiFeedback));
        Invoke(nameof(NascondiFeedback), 2f);
    }

    private void NascondiFeedback() => feedbackText.gameObject.SetActive(false);

    private void MostraAnchorExplanation(bool corretta)
    {
        string reason = GeneraSpiegazioneRuleBased(pazienteCorrente);

        anchorText.text = corretta
            ? $"CORRETTO\n{reason}"
            : $"ERRATO\n{reason}";

        anchorText.gameObject.SetActive(true);

        // tienilo visibile finché serve
        // CancelInvoke(nameof(NascondiAnchor));
        // Invoke(nameof(NascondiAnchor), 4f);
    }

    private void NascondiAnchor() => anchorText.gameObject.SetActive(false);

    private string GeneraSpiegazioneRuleBased(CartellaClinica p)
    {
        List<string> motivi = new List<string>();

        // Età
        motivi.Add($"Età: {p.RIDAGEYR} anni");

        // Sesso
        string sesso = p.RIAGENDR;
        motivi.Add($"Sesso: {sesso}");

        // Glucosio a digiuno
        if (p.LBXGLU >= 126)
            motivi.Add($"Glucosio elevato: {p.LBXGLU} mg/dL ≥ 126 (soglia per diabete)");
        else if (p.LBXGLU >= 100)
            motivi.Add($"Glucosio borderline: {p.LBXGLU} mg/dL (range prediabete)");
        else
            motivi.Add($"Glucosio normale: {p.LBXGLU} mg/dL");

        // Insulina
        if (p.LBXIN > 25)
            motivi.Add($"Insulina elevata: {p.LBXIN} µU/mL – possibile insulino-resistenza");
        else if (p.LBXIN < 2)
            motivi.Add($"Insulina molto bassa: {p.LBXIN} µU/mL – possibile ipoproduzione pancreatica");
        else
            motivi.Add($"Livelli di insulina nella norma: {p.LBXIN} µU/mL");

        // BMI
        if (p.BMXBMI >= 30)
            motivi.Add($"Obesità (BMI = {p.BMXBMI:F1}): forte rischio metabolico");
        else if (p.BMXBMI >= 25)
            motivi.Add($"Sovrappeso (BMI = {p.BMXBMI:F1}): moderato rischio");
        else if (p.BMXBMI < 18.5)
            motivi.Add($"Sottopeso (BMI = {p.BMXBMI:F1}): non direttamente correlato ma da monitorare");
        else
            motivi.Add($"BMI nella norma: {p.BMXBMI:F1}");

        // Etichetta finale in base alla previsione
        string conclusione;
        switch (p.DIQ010)
        {
            case "Yes":
                conclusione = "Il paziente è DIABETICO. Fattori che supportano la diagnosi:";
                break;
            case "No":
                conclusione = "Il paziente NON ha il diabete. Parametri analizzati:";
                break;
            case "Borderline":
                conclusione = "Il paziente è in una condizione BORDERLINE. Possibili segnali di rischio:";
                break;
            default:
                conclusione = "Diagnosi sconosciuta. Parametri disponibili:";
            break;

        }/*
        string conclusione = p.DIQ010 switch
        {
            1 => "Il paziente è DIABETICO. Fattori che supportano la diagnosi:",
            2 => "Il paziente NON ha il diabete. Parametri analizzati:",
            3 => "Il paziente è in una condizione BORDERLINE. Possibili segnali di rischio:",
            _ => "Diagnosi sconosciuta. Parametri disponibili:"
        };*/

        return conclusione + "\n" + string.Join("\n", motivi);
    }


    // ──────────────────────────────────────────────────────────────
    // Getter utili (se servono ad altri script)
    public int GetPunteggio() => punteggio;
    public int GetDiagnosiEseguite() => diagnosiEseguite;
}
