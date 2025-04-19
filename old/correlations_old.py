import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from plot_ck import get_aggregated_metrics
from repo_utils import get_repo_id

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def correlate(corr_method, df_merged, agg_function):
    # Definir las métricas CK que te interesan
    ck_metrics = ['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']

    # Calcular la correlación con ROLLBACK_RATIO
    correlations = {}
    for metric in ck_metrics:
        if df_merged[metric].nunique() > 1 and df_merged['ROLLBACK_RATIO'].nunique() > 1:
            # Calcular la correlación solo si ambas columnas tienen más de un valor único
            correlations[metric] = df_merged[metric].corr(df_merged['ROLLBACK_RATIO'], method=corr_method)
        else:
            # Si la columna es constante, asignar NaN
            correlations[metric] = float('nan')

    # Crear un DataFrame para visualización
    corr_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['CORR_ROLLBACK_RATIO'])
    corr_df.index.name = 'METRIC'
    corr_df.reset_index(inplace=True)
    corr_df["AGG_FUNCTION"] = agg_function
    corr_df["CORR_METHOD"] = corr_method
    return corr_df

def repo_correlations(df_ck_repo, df_deploys_repo, app_name):
    df_ck_repo_median, df_ck_repo_mean, df_ck_repo_wavg = get_aggregated_metrics(df_ck_repo)
    df_rollback_ratio = df_deploys_repo[['YEAR_MONTH', 'ROLLBACK_RATIO']]    

    # Unir ambos dataframes en base al mes
    df_merged_median = pd.merge(df_ck_repo_median, df_rollback_ratio, on='YEAR_MONTH', how='inner')
    df_merged_mean = pd.merge(df_ck_repo_mean, df_rollback_ratio, on='YEAR_MONTH', how='inner')
    df_merged_wavg = pd.merge(df_ck_repo_wavg, df_rollback_ratio, on='YEAR_MONTH', how='inner')

    corr_methods = ["pearson", "kendall", "spearman"]
    corr_repo = pd.DataFrame()
    for corr_method in corr_methods:
        corr_median = correlate(corr_method, df_merged_median, 'median')
        corr_mean = correlate(corr_method, df_merged_mean, 'mean')
        corr_wavg = correlate(corr_method, df_merged_wavg, 'weighted_avg')
        corr_repo = pd.concat([corr_repo, corr_median, corr_mean, corr_wavg], ignore_index=True)
        
    corr_repo["APPLICATION_NAME"] = get_repo_id(app_name)
    return corr_repo 


def correlations():
    df_ck = pd.read_csv(f"./datasets/apps_ck_monthly.csv")
    df_ck['YEAR_MONTH'] = pd.to_datetime(df_ck['YEAR_MONTH'])
 
    df_deploys = pd.read_csv(f"./datasets/apps_deploys_monthly.csv")
    df_deploys['YEAR_MONTH'] = pd.to_datetime(df_deploys['YEAR_MONTH'])
    
    apps = pd.read_csv(f"./datasets/applications.csv")
    #apps = apps[apps['APPLICATION_NAME'] == 'sp-activities-api']
    corrs_df = pd.DataFrame()
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df_ck_repo = df_ck[df_ck['APPLICATION_NAME'] == app_name]
        df_deploys_repo = df_deploys[df_deploys['APPLICATION_NAME'] == app_name]
        logging.info(f"Generating correlations for {app_name}")
        repo_corrs_df = repo_correlations(df_ck_repo, df_deploys_repo, app_name)
        logging.info(f"Finished correlations for {app_name}")
        corrs_df = pd.concat([corrs_df, repo_corrs_df], ignore_index=True)

    corrs_df.to_csv(f"./datasets/apps_correlations.csv", index=False)

def main():
    # Configurar el tamaño de fuente global
    #plt.rcParams.update({'font.size': 14})
    correlations()


if __name__ == "__main__":
    main()

