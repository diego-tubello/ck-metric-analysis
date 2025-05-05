import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # Configurar el tamaño de fuente global
    plt.rcParams.update({'font.size': 16})

    df = pd.read_csv("./datasets/apps_ck_monthly.csv")
    df = df[df['YEAR_MONTH'] == '2025-01-01']
    df = df[df['APPLICATION_NAME'] == 'prepaid-api']
    df = df[['class', 'wmc', 'dit', 'noc', 'cbo', 'rfc', 'lcom']]
    df.columns = df.columns.str.upper()

    metrics = ['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']

    _, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    for ax, metric in zip(axes, metrics):
        sns.histplot(df[metric], bins=50, kde=True, ax=ax, edgecolor='black')
        ax.set_title(f'Histograma {metric}')
        ax.set_xlabel(metric)
        ax.set_ylabel('Frecuencia')
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('./plots/histograma_ejemplo.png')
    plt.close()


if __name__ == "__main__":
    main()
