using UnityEngine;
using System.Collections.Generic;


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


    //Per l'estrazione delle tuple casuali
    private List<int> indiciMescolati;
    private int indiceCorrente = 0;

    public void InizializzaDopoCaricamento()
    {
        if(datasetLoader != null && datasetLoader.pazienti.Count > 0)
        {
            indiciMescolati = new List<int>();
            for (int i = 0; i < datasetLoader.pazienti.Count; i++)
            {
                indiciMescolati.Add(i);
            }
            //Mescola la lista
            Shuffle(indiciMescolati);
            Debug.Log("Indici mescolati da Shuffle:"); 
            for(int i=0;i<indiciMescolati.Count;i++)
            {
                Debug.Log($"indiciMescolati[{i}] = {indiciMescolati[i]}");
            }
        }else
        {
            Debug.LogError("[SpawnPaziente] DatasetLoader non assegnato.");
        }
    }

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
        //int indiceDati = Random.Range(0, datasetLoader.pazienti.Count);


        Debug.Log(" PAZIENTI TRA CUI SCEGLIERE");
        for (int i = 0; i < datasetLoader.pazienti.Count; i++)
        {
            Debug.Log($"datasetLoader.pazienti[{i}] = {datasetLoader.pazienti[i].SEQN}");
        }

        //Problema: i primi 10 pazienti hanno SEQN = 0
        /* Va da:
        - datasetLoader.pazienti[0] = 0
        fino a 10 sono tutti a 0 per poi da
        - datasetLoader.pazienti[10] = 130378
        fino a 
        - datasetLoader.pazienti[3492] = 142309
        */

        if (indiciMescolati == null)
        {
            Debug.LogWarning("[SpawnPaziente] Lista indici mescolati non inizializzata o indice corrente a 0.");
            return;
        }

        if (indiceCorrente >= indiciMescolati.Count)
        {
            //Se ho finito la lista, la rimescolo e ricomincio
            Shuffle(indiciMescolati);
            indiceCorrente = 0;
        }

        int indiceDati = indiciMescolati[indiceCorrente];
        indiceCorrente++;
        CartellaClinica dati = datasetLoader.pazienti[indiceDati];
        Debug.Log($"[SpawnPaziente] Paziente selezionato: SEQN = {dati.SEQN}, RIDAGEYR = {dati.RIDAGEYR}, RIAGENDR = {dati.RIAGENDR}");

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

        // Metodo per mescolare una lista in modo casuale

    }
    /*
    È un’implementazione del Fisher–Yates Shuffle, un algoritmo che:
    - scorre la lista da fine a inizio,
    - a ogni passo scambia l’elemento corrente con un altro scelto casualmente,
    - garantendo che ogni permutazione sia equiprobabile.
    */

    private void Shuffle<T>(List<T> list)
    {
        System.Random rng = new System.Random(); // Generatore di numeri casuali
        int n = list.Count;
        while (n > 1)
        {
            n--;
            int k = rng.Next(n + 1); // Estrae un indice casuale tra 0 e n
            T value = list[k];
            list[k] = list[n];
            list[n] = value;
        } 
    }
}
