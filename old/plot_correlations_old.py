import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from correlations import correlate_apps, correlate_groups

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_by_group_all(corrs_df, grouping_column, output_dir):
    sns.set(style="whitegrid")
    agg_functions = corrs_df["AGG_FUNCTION"].unique()
    corr_methods = corrs_df["CORR_METHOD"].unique()
    groups = corrs_df[grouping_column].unique()

    for agg in agg_functions:
        for method in corr_methods:
            for group in groups:
                df_plot = corrs_df[
                    (corrs_df["AGG_FUNCTION"] == agg) &
                    (corrs_df["CORR_METHOD"] == method) &
                    (corrs_df[grouping_column] == group)
                ]
                if df_plot.empty:
                    continue

                plt.figure(figsize=(10, 6))
                sns.barplot(
                    data=df_plot,
                    x="METRIC",
                    y="CORR_ROLLBACK_RATIO",
                    hue="TARGET",
                    palette="muted"
                )
                plt.title(f"Grupo {group} - Correlación CK vs ROLLBACK ({agg}, {method})")
                plt.ylabel("Coeficiente de correlación")
                plt.xlabel("Métrica CK")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.legend(title="Tipo de correlación")
                plt.ylim(-1.0, 1.0)
                plt.grid(axis='y')

                filename = f"{output_dir}/ck_corr_{group}_{method}_{agg}.png"
                plt.savefig(filename)
                plt.close()
                logging.info(f"Gráfico guardado: {filename}")


# === Main ===

def main():
    groups_corrs = correlate_groups()
    plot_by_group_all(groups_corrs, 'GROUP', './plots/correlations/groups')

    #app_corrs = correlate_apps()
    #plot_by_group_all(app_corrs, 'APPLICATION_NAME', './plots/correlations/apps')


if __name__ == "__main__":
    main()
