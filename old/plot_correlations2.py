import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from correlations import correlate_apps, correlate_groups

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_by_group_and_target(corrs_df, grouping_column, output_dir):
    sns.set(style="whitegrid")
    agg_functions = corrs_df["AGG_FUNCTION"].unique()
    corr_methods = corrs_df["CORR_METHOD"].unique()
    groups = corrs_df[grouping_column].unique()
    targets = corrs_df["TARGET"].unique()  # Añadido para iterar sobre los targets

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

    # Iterar sobre los grupos y los targets
    for group in groups:
        for target in targets:
            fig, axes = plt.subplots(len(corr_methods), len(agg_functions), figsize=(5 * len(agg_functions), 4 * len(corr_methods)), sharey=True)
            fig.suptitle(f'Correlación CK vs Tasa de Rollbacks - Grupo {group} - TARGET {target}', fontsize=16)

            for i, method in enumerate(corr_methods):
                for j, agg in enumerate(agg_functions):
                    ax = axes[i][j] if len(corr_methods) > 1 else axes[j]
                    df_plot = corrs_df[
                        (corrs_df[grouping_column] == group) &
                        (corrs_df["TARGET"] == target) &
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

            # Agregar una única leyenda general abajo
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center', ncol=len(labels), title="TARGET")

            fig.tight_layout(rect=[0, 0.05, 1, 0.95])  # Ajuste para dejar espacio a la leyenda y título
            filename = f"{output_dir}/ck_corr_group_{group}_target_{target}.png"
            fig.savefig(filename)
            plt.close(fig)
            logging.info(f"Gráfico guardado: {filename}")

# === Main ===

def main():
    groups_corrs = correlate_groups()
    plot_by_group_and_target(groups_corrs, 'GROUP', './plots/correlations/groups')

    # app_corrs = correlate_apps()
    # plot_by_group_and_target(app_corrs, 'APPLICATION_NAME', './plots/correlations/apps')

if __name__ == "__main__":
    main()
