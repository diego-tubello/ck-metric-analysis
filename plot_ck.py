import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from repo_utils import get_repo_id

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Definir la función de promedio ponderado
def weighted_average(group, value_col, weight_col):
    return (group[value_col] * group[weight_col]).sum() / group[weight_col].sum()

def get_aggregated_metrics(df_ck_repo):
    df = df_ck_repo
    # Strip any leading or trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Remove any rows where the type is enum
    df = df[df['type'] != 'enum']
    # Remove any rows where the class name contains ".dto." 
    df = df[~df['class'].str.contains('.dto.')]

    df = df[['YEAR_MONTH', 'tag_name', 'class', 'wmc', 'dit', 'noc', 'cbo', 'rfc', 'lcom', 'loc']]
    df.columns = ['YEAR_MONTH', 'TAG_NAME', 'CLASS_NAME', 'WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM', 'LOC']
    df['YEAR_MONTH'] = pd.to_datetime(df['YEAR_MONTH'])

    grouped_metrics_by_date = df.groupby('YEAR_MONTH')[['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']]

    median_by_date = grouped_metrics_by_date.median()
    mean_by_date = grouped_metrics_by_date.mean()
  
    # Crear un diccionario de funciones de agregación
    agg_funcs = {metric: lambda x, col=metric: weighted_average(df.loc[x.index], col, 'LOC') 
                for metric in ['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']}

    # Calcular el promedio ponderado por fecha usando groupby y agg
    weighted_avg_by_date = grouped_metrics_by_date.agg(agg_funcs)

    return median_by_date, mean_by_date, weighted_avg_by_date
  

def plot_values_over_time(title, date_range, values_by_date, filename):
    plt.figure(figsize=(12, 6))
    for column in values_by_date.columns:
        plt.plot(values_by_date.index, values_by_date[column], label=column)

    plt.title(title)
    plt.xlabel('Fecha')
    plt.ylabel('Valor')
    plt.xticks(date_range, date_range.strftime('%Y-%m'), rotation=90)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'./plots/timeseries/{filename}.png')
    plt.close()

def plot_repo_ck_over_time(df_ck_repo, repo_name, date_range):
    median_by_date, mean_by_date, weighted_avg_by_date = get_aggregated_metrics(df_ck_repo)
    plot_values_over_time(f'CK [Mediana] - {get_repo_id(repo_name)}', date_range, median_by_date, f'{repo_name}_ck_median')
    plot_values_over_time(f'CK [Media] - {get_repo_id(repo_name)}', date_range, mean_by_date, f'{repo_name}_ck_mean')
    plot_values_over_time(f'CK [Media Ponderada] - {get_repo_id(repo_name)}', date_range, weighted_avg_by_date, f'{repo_name}_ck_weighted_avg')


def plot_ck_over_time(date_range):
    df_ck = pd.read_csv(f"./datasets/apps_ck_monthly.csv")
    apps = pd.read_csv(f"./datasets/applications.csv")
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df_repo = df_ck[df_ck['APPLICATION_NAME'] == app_name]
        logging.info(f"Generating plots for {app_name}")
        plot_repo_ck_over_time(df_repo, app_name, date_range)
        logging.info(f"Finished plots for {app_name}")

