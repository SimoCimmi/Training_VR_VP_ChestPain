using TMPro;
using UnityEngine;

public class CartellaUI : MonoBehaviour
{
    public static CartellaUI Instance;

    public GameObject pannello;
    public TMP_Text txtID, txtEta, txtSesso, txtBMI, txtGlucosio, txtInsulina;

    private void Awake()
    {
        Instance = this;
        pannello.SetActive(false);  // nascosta all'inizio
    }

    public void Mostra(CartellaClinica c)
    {
        pannello.SetActive(true);

        txtID.text = $"ID: {c.SEQN}";
        txtEta.text = $"Age: {c.RIDAGEYR}";
        txtSesso.text = $"Gender: {c.RIAGENDR}";
        txtBMI.text = $"BMI: {c.BMXBMI:F1}";
        txtGlucosio.text = $"Fasting glucose: {c.LBXGLU:F1} mg/dL";
        txtInsulina.text = $"Insulin level: {c.LBXIN:F1} µU/mL";;
    }

    public void Nascondi()
    {
        pannello.SetActive(false);
    }
}

