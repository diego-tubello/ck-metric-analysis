import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

from plot_ck import get_aggregated_metrics

# === 1. Cargar los datasets ===
df_ck = pd.read_csv('./datasets/apps_ck_monthly.csv')
df_ck_median, df_ck_mean, df_ck_wavg = get_aggregated_metrics(df_ck)
df_ck = df_ck_wavg.reset_index()

df_deploys = pd.read_csv('./datasets/apps_deploys_monthly.csv')
df_groups = pd.read_csv('./datasets/applications_stats.csv')  # Debe tener APPLICATION_NAME y GROUP
df_groups = df_groups.rename(columns={'APPLICATION_NAME': 'APPLICATION_NAME', 'group': 'GROUP'})
df_groups = df_groups[['APPLICATION_NAME', 'GROUP']]

# Asegurar tipos de fecha
df_ck['YEAR_MONTH'] = pd.to_datetime(df_ck['YEAR_MONTH'])
df_deploys['YEAR_MONTH'] = pd.to_datetime(df_deploys['YEAR_MONTH'])

# Agregar rollback del mes siguiente
df_deploys = df_deploys.sort_values(by=['APPLICATION_NAME', 'YEAR_MONTH'])
df_deploys['ROLLBACK_RATIO_NEXT_MONTH'] = df_deploys.groupby('APPLICATION_NAME')['ROLLBACK_RATIO'].shift(-1)

# === 2. Merge de datasets ===

df = pd.merge(df_ck, df_deploys, on=['APPLICATION_NAME', 'YEAR_MONTH'], how='inner')

df = pd.merge(df, df_groups, on='APPLICATION_NAME', how='left')

# === 3. Crear carpetas de salida ===
output_dir = './plots/scatter_por_grupo'
os.makedirs(output_dir, exist_ok=True)

# === 4. Graficar por grupo ===

ck_metrics = ['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']
targets = ['ROLLBACK_RATIO', 'ROLLBACK_RATIO_NEXT_MONTH']

for group in df['GROUP'].dropna().unique():
    df_group = df[df['GROUP'] == group]

    for metric in ck_metrics:
        for target in targets:
            plt.figure(figsize=(8, 6))
            sns.regplot(data=df_group, x=metric, y=target,
                        scatter_kws={'alpha': 0.5, 's': 60}, ci=None, line_kws={'color': 'red'})
            
            plt.title(f'Grupo {group} - {metric} vs {target}')
            plt.xlabel(metric)
            plt.ylabel(target)
            plt.grid(True)
            plt.tight_layout()
            
            # Guardar
            filename = f'grupo_{group}_{metric}_vs_{target}.png'.lower().replace(' ', '_')
            plt.savefig(os.path.join(output_dir, filename))
            plt.close()
