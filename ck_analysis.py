import datetime
import subprocess
from git import Repo
import pandas as pd
import logging
import os
from repo_utils import get_repo_id, run_metric_all_versions, REPOS_BASE_PATH

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OUTPUT_PATH = "output"
TEMP_PATH = f"{OUTPUT_PATH}/temp/"

def run_ck(repo_path):
    try:
        command = ["java", "-jar", "./jars/ck-0.7.1.jar", repo_path, "false", "0", "false", TEMP_PATH]
        subprocess.run(command, capture_output=True, text=True, check=True)
        results_df = pd.read_csv(f"{TEMP_PATH}class.csv")
        results_df = results_df.drop(columns=["file"])
        results_df["class"] = results_df["class"].replace(to_replace=r"^(?:\w+\.){2}", value="com.company.", regex=True)

        os.remove(f"{TEMP_PATH}class.csv")
        os.remove(f"{TEMP_PATH}method.csv")
        return results_df
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error executing JAR: {e.stderr}") from e
    

def run_ck_master(repo_name):
    repo_id = get_repo_id(repo_name)
    repo_path = f"{REPOS_BASE_PATH}/{repo_name}"

    # Abrir el repositorio
    repo = Repo(repo_path)
    repo.git.checkout("master")

    results_df = run_ck(repo_path)
    
    # Guardar el DataFrame final a un archivo CSV
    final_output_path = f"{OUTPUT_PATH}/master/{repo_id}.csv"
    results_df.to_csv(final_output_path, index=False)
    logging.info(f"Results saved to {final_output_path}")


def run_ck_master_all_repos():
    folders = os.listdir(REPOS_BASE_PATH)
    for repo_name in folders:
        run_ck_master(repo_name)


def run_ck_verions_all_repos():
    apps = pd.read_csv(f"./datasets/applications.csv")
    
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2025, 2, 28)
    output_path = f'{OUTPUT_PATH}/ck_versioned'

    for index, app in apps.iterrows():
        run_metric_all_versions(app["APPLICATION_NAME"], output_path, start_date, end_date, run_ck)


def combine_results():
    combined_df = pd.DataFrame()
    apps = pd.read_csv(f"./datasets/applications.csv")
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df = pd.read_csv(f"{OUTPUT_PATH}/ck_versioned/{app_name}.csv")
        df['APPLICATION_NAME'] = app_name
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    combined_output_path = f"{OUTPUT_PATH}/ck_versioned/ck_apps_versions.csv"
    combined_df.to_csv(combined_output_path, index=False)

def combine_results():
    combined_df = pd.DataFrame()
    apps = pd.read_csv(f"./datasets/apps_ck_versions.csv")
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df = pd.read_csv(f"{OUTPUT_PATH}/ck_versioned/{app_name}.csv")
        df['APPLICATION_NAME'] = app_name
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    combined_output_path = f"{OUTPUT_PATH}/ck_versioned/ck_apps_versions.csv"
    combined_df.to_csv(combined_output_path, index=False)


def keep_last_tag_per_month():
    df = pd.read_csv(f"./datasets/apps_ck_versions.csv")

    df_tags = df[['APPLICATION_NAME', 'tag_date', 'tag_name']].drop_duplicates().reset_index(drop=True)
    df_tags['YEAR_MONTH'] = pd.to_datetime(df_tags['tag_date'].str[:7], format='%Y-%m')

    df_month_last_tag = df_tags.sort_values('tag_date').groupby(['APPLICATION_NAME', 'YEAR_MONTH']).last().reset_index()

    df_merged = pd.merge(
        df_month_last_tag[['APPLICATION_NAME', 'YEAR_MONTH', 'tag_name']],
        df,
        on=['APPLICATION_NAME', 'tag_name'],
        how='inner'  # Usar inner join para conservar solo las filas coincidentes
    )

    df_merged = df_merged.drop(columns=['tag_date'])

    df_merged.to_csv(f"./datasets/apps_ck_monthly.csv", index=False)


def main():
    run_ck_verions_all_repos()
    combine_results()
    keep_last_tag_per_month()



if __name__ == "__main__":
    main()
