import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- 1. CONFIGURAZIONE PERCORSI E STILE ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, "Final_Reports/Raw_HumanEvaluations_CSV.csv")

sns.set_theme(style="whitegrid")
METRICS = ['IF', 'F', 'EAR', 'N', 'S']
METRIC_LABELS = ['Instruction Following', 'Faithfulness', 'Empathy', 'Naturalness', 'Sensibleness']
MODEL_PALETTE = sns.color_palette("muted", 4)


def create_radar_chart(ax, angles, values, label, color):
    values = np.concatenate((values, [values[0]]))
    ax.plot(angles, values, color=color, linewidth=2, label=label)
    ax.fill(angles, values, color=color, alpha=0.25)


def generate_human_charts():
    if not os.path.exists(INPUT_CSV):
        print(f"Errore: Non trovo il file {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV, sep=';')
    df.columns = df.columns.str.strip()
    df['LLM'] = df['LLM'].str.strip()
    df['Global_Score'] = df[METRICS].mean(axis=1)

    llms = df['LLM'].dropna().unique()

    # --- 2. GRAFICI INDIVIDUALI UMANI (Nelle cartelle esistenti dei modelli) ---
    for i, llm in enumerate(llms):
        print(f"Generando grafici umani per {llm}...")
        llm_dir = os.path.join(SCRIPT_DIR, f"{llm}_Reports")
        os.makedirs(llm_dir, exist_ok=True)

        df_llm = df[df['LLM'] == llm]

        # A. Radar Chart Umano
        fig_radar = plt.figure(figsize=(8, 8))
        ax = fig_radar.add_subplot(111, polar=True)
        angles = np.linspace(0, 2 * np.pi, len(METRICS), endpoint=False).tolist()
        angles += angles[:1]

        avg_values = df_llm[METRICS].mean().values
        create_radar_chart(ax, angles, avg_values, f"{llm} (Umano)", MODEL_PALETTE[i % 4])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(METRIC_LABELS, size=10)
        ax.set_ylim(0, 5)
        plt.title(f"Profilo Prestazionale Umano: {llm}", size=15, pad=20)
        plt.savefig(os.path.join(llm_dir, f"Human_{llm}_RadarChart.png"), dpi=300, bbox_inches='tight')
        plt.close()

        # B. Box Plot Umano
        plt.figure(figsize=(10, 6))
        df_melted = df_llm.melt(value_vars=METRICS, var_name='Metrica', value_name='Voto')

        ax_box = sns.boxplot(
            x='Metrica',
            y='Voto',
            data=df_melted,
            hue='Metrica',
            palette="Oranges",
            legend=False
        )
        ax_box.set_xticks(range(len(METRICS)))
        ax_box.set_xticklabels(METRIC_LABELS)

        plt.title(f"Distribuzione Voti Umani e Affidabilità: {llm}", size=14)
        plt.ylim(0, 6)
        plt.savefig(os.path.join(llm_dir, f"Human_{llm}_BoxPlot.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # --- 3. GRAFICI COMPARATIVI UMANI (In Final_Reports) ---
    print("Generando grafici comparativi umani globali...")

    # C. Grouped Bar Chart Umano
    avg_total = df.groupby('LLM')[METRICS].mean().reset_index()
    avg_melted = avg_total.melt(id_vars='LLM', var_name='Metrica', value_name='Media')

    plt.figure(figsize=(12, 7))
    sns.barplot(x='Metrica', y='Media', hue='LLM', data=avg_melted, palette="muted")
    plt.title("Confronto Umano Testa a Testa: LLM vs Metriche", size=16)
    plt.xticks(ticks=range(len(METRICS)), labels=METRIC_LABELS)
    plt.ylim(0, 5.5)
    plt.legend(title="Modelli", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(os.path.join(SCRIPT_DIR, "Final_Reports/Final_Human_Comparison_Bars.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # D. Heatmap Umana (Casi Clinici)
    pivot_heatmap = df.pivot_table(index='Case_ID', columns='LLM', values='Global_Score', aggfunc='mean')

    plt.figure(figsize=(10, 12))
    sns.heatmap(pivot_heatmap, annot=True, cmap="OrRd", fmt=".1f", cbar_kws={'label': 'Media Global Score Umano'})
    plt.title("Heatmap Umana: Performance per Caso Clinico", size=16)
    plt.ylabel("ID Caso Clinico")
    plt.xlabel("Modello LLM")
    plt.savefig(os.path.join(SCRIPT_DIR, "Final_Reports/Final_Human_Heatmap_Cases.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print("\n Tutti i grafici basati sulle valutazioni umane sono pronti!")


if __name__ == "__main__":
    generate_human_charts()