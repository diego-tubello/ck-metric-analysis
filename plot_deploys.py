import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import numpy as np
from repo_utils import get_repo_id

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_repo_deploys_over_time(df_repo, repo_name, date_range):
    df = df_repo.copy()

    # Asegurar formato correcto de fechas
    df['YEAR_MONTH'] = pd.to_datetime(df['YEAR_MONTH'])
    df = df.sort_values('YEAR_MONTH').reset_index(drop=True)

    x = np.arange(len(df))

    fig, ax1 = plt.subplots(figsize=(12, 6))

    finished_color = '#6A9C76'      
    rollbacked_color = '#D35F5F'
    ratio_line_color = 'firebrick'

    # Barras apiladas
    ax1.bar(x, df['FINISHED_COUNT'], label='Finalizados', color=finished_color)
    ax1.bar(x, df['ROLLBACKED_COUNT'], bottom=df['FINISHED_COUNT'], label='Rollbacks', color=rollbacked_color)

    for i in range(len(df)):
        finished = df['FINISHED_COUNT'][i]
        rollbacked = df['ROLLBACKED_COUNT'][i]
        if finished > 0:
            ax1.text(x[i], finished / 2, f"{int(finished)}", ha='center', va='center', fontsize=10, color='black')
        if rollbacked > 0:
            ax1.text(x[i], finished + rollbacked / 2, f"{int(rollbacked)}", ha='center', va='center', fontsize=10, color='black')

    # Eje secundario para rollback ratio
    ax2 = ax1.twinx()
    ax2.plot(x, df['ROLLBACK_RATIO'], color=ratio_line_color, marker='o', label='Tasa de Rollbacks')
    ax2.set_ylabel('Tasa de Rollbacks', color=ratio_line_color)
    ax2.tick_params(axis='y', labelcolor=ratio_line_color)
    ax2.set_ylim(0, 1)

    ax1.set_xticks(ticks=x)
    ax1.set_xticklabels(df['YEAR_MONTH'].dt.strftime('%Y-%m'), rotation=90)

    ax1.set_title(f'Deploys - {get_repo_id(repo_name)}')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('# Deploys')
    ax1.grid(axis='y')

    # Combinar leyendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.tight_layout()
    plt.savefig(f'./plots/timeseries/{repo_name}_deploys.png')
    plt.close()


def plot_deploys_over_time(date_range):
    df_deploys = pd.read_csv(f"./datasets/apps_deploys_monthly.csv")
    #filter date range
    df_deploys['YEAR_MONTH'] = pd.to_datetime(df_deploys['YEAR_MONTH'])
    df_deploys = df_deploys[(df_deploys['YEAR_MONTH'] >= date_range.min()) & (df_deploys['YEAR_MONTH'] <= date_range.max())]
    apps = pd.read_csv(f"./datasets/applications.csv")
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df_repo = df_deploys[df_deploys['APPLICATION_NAME'] == app_name]
        logging.info(f"Generating plots for {app_name}")
        plot_repo_deploys_over_time(df_repo, app_name, date_range)
        logging.info(f"Finished plots for {app_name}")

