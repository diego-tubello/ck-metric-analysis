import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from correlations import correlate_apps, correlate_groups

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_by_group_all(corrs_df, grouping_column, output_dir):
    sns.set(style="whitegrid")
    plt.rcParams.update({'font.size': 14}) 
    agg_functions = corrs_df["AGG_FUNCTION"].unique()
    corr_methods = corrs_df["CORR_METHOD"].unique()
    groups = corrs_df[grouping_column].unique()

    corr_methods = {
        "pearson": "Pearson",
        "kendall": "Kendall",
        "spearman": "Spearman"
    }

    agg_functions = {
        "median": "Mediana",
        "mean": "Media",
        "weighted_avg": "Promedio Ponderado"
    }

    targets = {
        "ROLLBACK_RATIO": "Mes Actual",
        "ROLLBACK_RATIO_NEXT_MONTH": "Mes Siguiente"
    }

    n_rows = len(corr_methods)
    n_cols = len(agg_functions)

    for group in groups:
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows), sharey=True)
        fig.suptitle(f'Correlación CK vs Tasa de Rollbacks - Grupo {group}', fontsize=20)

        for i, method in enumerate(corr_methods):
            for j, agg in enumerate(agg_functions):
                ax = axes[i][j] if n_rows > 1 else axes[j]
                df_plot = corrs_df[
                    (corrs_df[grouping_column] == group) &
                    (corrs_df["AGG_FUNCTION"] == agg) &
                    (corrs_df["CORR_METHOD"] == method)
                ]
                if df_plot.empty:
                    ax.axis('off')
                    continue

                sns.barplot(
                    data=df_plot,
                    x="METRIC",
                    y="CORR_ROLLBACK_RATIO",
                    hue="TARGET",
                    palette="muted",
                    ax=ax
                )
                if i == 0:
                    ax.set_title(agg_functions[agg])
                if j == 0:
                    ax.set_ylabel(corr_methods[method])
                else:
                    ax.set_ylabel("")
                ax.set_xlabel("")
                ax.set_ylim(-1, 1)
                ax.tick_params(axis='x', rotation=45)

                # Ocultar leyendas individuales
                ax.get_legend().remove()

        handles, labels = ax.get_legend_handles_labels()
        labels = [targets.get(label, label) for label in labels]
        fig.legend(handles, labels, loc='lower center', ncol=len(labels))

        fig.tight_layout(rect=[0, 0.05, 1, 0.95])  # Ajuste para dejar espacio a la leyenda y título
        filename = f"{output_dir}/ck_corr_group_{group}.png"
        fig.savefig(filename)
        plt.close(fig)
        logging.info(f"Gráfico guardado: {filename}")

# === Main ===

def main():
    groups_corrs = correlate_groups()
    plot_by_group_all(groups_corrs, 'GROUP', './plots/correlations/groups')

    app_corrs = correlate_apps()
    plot_by_group_all(app_corrs, 'APPLICATION_NAME', './plots/correlations/apps')


if __name__ == "__main__":
    main()
