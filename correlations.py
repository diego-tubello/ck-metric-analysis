import pandas as pd
import logging
from plot_ck import get_aggregated_metrics
from repo_utils import get_repo_id

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Cálculo de correlaciones ===
def correlate(corr_method, df_merged, agg_function, target_column='ROLLBACK_RATIO'):
    ck_metrics = ['WMC', 'DIT', 'NOC', 'CBO', 'RFC', 'LCOM']
    correlations = {}
    for metric in ck_metrics:
        if metric in df_merged.columns and target_column in df_merged.columns:
            if df_merged[metric].nunique() > 1 and df_merged[target_column].nunique() > 1:
                correlations[metric] = df_merged[metric].corr(df_merged[target_column], method=corr_method)
            else:
                correlations[metric] = float('nan')
    corr_df = pd.DataFrame.from_dict(correlations, orient='index', columns=['CORR_ROLLBACK_RATIO'])
    corr_df.index.name = 'METRIC'
    corr_df.reset_index(inplace=True)
    corr_df["AGG_FUNCTION"] = agg_function
    corr_df["CORR_METHOD"] = corr_method
    corr_df["TARGET"] = target_column
    return corr_df


def correlate_partition(df_ck_partition, df_deploys_partition, partition_name, partition):
    df_ck_median, df_ck_mean, df_ck_wavg = get_aggregated_metrics(df_ck_partition)

    df_deploys = df_deploys_partition[['YEAR_MONTH', 'ROLLBACK_RATIO']].copy()
    df_deploys['ROLLBACK_RATIO_NEXT_MONTH'] = df_deploys['ROLLBACK_RATIO'].shift(-1)

    deploy_cols = ['YEAR_MONTH', 'ROLLBACK_RATIO', 'ROLLBACK_RATIO_NEXT_MONTH']
    df_merged_median = pd.merge(df_ck_median, df_deploys[deploy_cols], on='YEAR_MONTH', how='inner')
    df_merged_mean = pd.merge(df_ck_mean,   df_deploys[deploy_cols], on='YEAR_MONTH', how='inner')
    df_merged_wavg = pd.merge(df_ck_wavg,   df_deploys[deploy_cols], on='YEAR_MONTH', how='inner')

    corr_methods = ["pearson", "kendall", "spearman"]
    corr_repo = pd.DataFrame()

    for method in corr_methods:
        for target in ['ROLLBACK_RATIO', 'ROLLBACK_RATIO_NEXT_MONTH']:
            corr_repo = pd.concat([
                corr_repo,
                correlate(method, df_merged_median, 'median', target),
                correlate(method, df_merged_mean, 'mean', target),
                correlate(method, df_merged_wavg, 'weighted_avg', target)
            ], ignore_index=True)

    corr_repo[partition_name] = partition
    return corr_repo


def correlate_apps():
    df_ck = pd.read_csv("./datasets/apps_ck_monthly.csv")
    df_ck['YEAR_MONTH'] = pd.to_datetime(df_ck['YEAR_MONTH'])

    df_deploys = pd.read_csv("./datasets/apps_deploys_monthly.csv")
    df_deploys['YEAR_MONTH'] = pd.to_datetime(df_deploys['YEAR_MONTH'])

    apps = pd.read_csv("./datasets/applications.csv")
    corrs_df = pd.DataFrame()

    for _, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df_ck_repo = df_ck[df_ck['APPLICATION_NAME'] == app_name]
        df_deploys_repo = df_deploys[df_deploys['APPLICATION_NAME'] == app_name]
        logging.info(f"Calculando correlaciones para {app_name}")
        repo_corrs_df = correlate_partition(df_ck_repo, df_deploys_repo, "APPLICATION_NAME", get_repo_id(app_name))
        corrs_df = pd.concat([corrs_df, repo_corrs_df], ignore_index=True)

    return corrs_df


def correlate_groups():
    df_ck = pd.read_csv("./datasets/apps_ck_monthly.csv")
    df_ck['YEAR_MONTH'] = pd.to_datetime(df_ck['YEAR_MONTH'])

    df_deploys = pd.read_csv("./datasets/apps_deploys_monthly.csv")
    df_deploys['YEAR_MONTH'] = pd.to_datetime(df_deploys['YEAR_MONTH'])

    apps = pd.read_csv("./datasets/applications_stats.csv")
    groups = apps["group"].unique()
    corrs_df = pd.DataFrame()

    for group in groups:
        group_apps = apps[apps["group"] == group]
        df_ck_group = df_ck[df_ck['APPLICATION_NAME'].isin(group_apps["APPLICATION_NAME"])]
        df_deploys_group = df_deploys[df_deploys['APPLICATION_NAME'].isin(group_apps["APPLICATION_NAME"])]

        logging.info(f"Calculando correlaciones para grupo: {group}")
        repo_corrs_df = correlate_partition(df_ck_group, df_deploys_group, 'GROUP', group)
        corrs_df = pd.concat([corrs_df, repo_corrs_df], ignore_index=True)

    return corrs_df


# === Main ===

def main():
    app_corrs = correlate_apps()
    app_corrs.to_csv("./datasets/correlations/apps_correlations.csv", index=False)
    logging.info("Correlaciones guardadas en apps_correlations.csv")
    
    
    group_corrs = correlate_groups()
    group_corrs.to_csv("./datasets/correlations/groups_correlations.csv", index=False)
    logging.info("Correlaciones guardadas en groups_correlations.csv")

if __name__ == "__main__":
    main()
