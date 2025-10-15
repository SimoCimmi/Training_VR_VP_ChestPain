using UnityEngine;

public class SpawnPaziente : MonoBehaviour
{
    [Header("Prefabs per sesso")]
    [SerializeField] private GameObject[] prefabMaschio;
    [SerializeField] private GameObject[] prefabFemmina;
    [SerializeField] private GameObject[] pazientiBambiniPrefab;

    [Header("Scene References")]
    [SerializeField] private Transform puntoSpawn;
    [SerializeField] private Transform puntoArrivo;
    [SerializeField] private DatasetLoader datasetLoader;
    [SerializeField] private DiagnosiManager diagnosiManager;


    [Header("Script collegato a LM Studio")]
    [SerializeField] private VirtualPatientManager virtualPatientManager;

    private GameObject pazienteCorrente;

    public void AttivaPortale()
    {
        // 1. Distrugge il paziente attuale se esiste
        if (pazienteCorrente != null)
        {
            Destroy(pazienteCorrente);
            CartellaUI.Instance.Nascondi();
        }

        // 2. Verifica dataset
        if (datasetLoader == null || datasetLoader.pazienti.Count == 0)
        {
            Debug.LogWarning("[SpawnPaziente] Dataset vuoto o loader mancante.");
            return;
        }

        // 3. Seleziona dati casuali da lista pazienti
        int indiceDati = Random.Range(0, datasetLoader.pazienti.Count);
        CartellaClinica dati = datasetLoader.pazienti[indiceDati];


        //3.1 Avvia paziente virtuale (LLM)    
        Debug.Log($"[SpawnPaziente] - virtualPatientManager = {virtualPatientManager}");
        if (virtualPatientManager != null)
        {
            Debug.Log("[SpawnPaziente] - Chiamo CreaPazienteVirtuale(dati)");
            virtualPatientManager.CreaPazienteVirtuale(dati);

        }

        // 4. Sceglie prefab in base al sesso
        GameObject prefabScelto = null;
        if (dati.RIDAGEYR < 16 && pazientiBambiniPrefab.Length > 0)
        {
            prefabScelto = pazientiBambiniPrefab[Random.Range(0, pazientiBambiniPrefab.Length)];
        }
        else
        {
            if (dati.RIAGENDR == 1 && prefabMaschio.Length > 0)
            {
                prefabScelto = prefabMaschio[Random.Range(0, prefabMaschio.Length)];
            }
            else if (dati.RIAGENDR == 2 && prefabFemmina.Length > 0)
            {
                prefabScelto = prefabFemmina[Random.Range(0, prefabFemmina.Length)];
            }
            else
            {
                Debug.LogWarning("[SpawnPaziente] Nessun prefab disponibile per il sesso indicato.");
                return;
            }
        }

        // 5. Istanzia prefab
        pazienteCorrente = Instantiate(prefabScelto, puntoSpawn.position, puntoSpawn.rotation);

        // 6. Inizializza movimento se presente
        if (pazienteCorrente.TryGetComponent(out PazienteMovimento movimento) && puntoArrivo != null)
        {
            movimento.destinazione = puntoArrivo;
        }

        // 7. Inizializza dati clinici
        if (pazienteCorrente.TryGetComponent(out Paziente pazienteScript))
        {
            pazienteScript.Inizializza(dati);
        }
        else
        {
            Debug.LogWarning("[SpawnPaziente] Script Paziente mancante nel prefab.");
        }

        // 8. Passa il paziente al DiagnosiManager
        if (diagnosiManager != null)
        {
            diagnosiManager.SetPazienteCorrente(dati);
        }
        else
        {
            Debug.LogWarning("[SpawnPaziente] DiagnosiManager non assegnato.");
        }
    }
}
