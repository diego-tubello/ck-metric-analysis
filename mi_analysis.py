import math
import datetime
import re
import subprocess
from git import Repo
import pandas as pd
import logging
import os
from repo_utils import get_repo_id, run_metric_all_versions

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPOS_BASE_PATH = "../repos"
OUTPUT_PATH = "output"
TEMP_PATH = f"{OUTPUT_PATH}/temp/"

def run_mant_index(repo_path):
    input_path = f"{repo_path}/src/main/java"
    output_path = f"{OUTPUT_PATH}/temp/results.csv"
    try:
        command = ["java", "-jar", "./jars/mant-index-1.0.1-all.jar", input_path, output_path]
        subprocess.run(command, capture_output=True, text=True, check=True)
        results_df = pd.read_csv(output_path)
        results_df["ClassName"] = results_df["ClassName"].replace(to_replace=r"^(?:\w+\.){2}", value="com.company.", regex=True)
        os.remove(output_path)
        return results_df
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing version: {e}")
        return pd.DataFrame()


def calculate_repo_mi(df):
    total_loc = df['loc'].sum()
    if total_loc > 0:
        mi = (df['mindex'] * df['loc']).sum() / total_loc
    else:
        mi = 0
    return mi


def run_mi_verions_all_repos():
    apps = pd.read_csv(f"./datasets/applications.csv")
    
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2025, 2, 28)
    output_path = f'{OUTPUT_PATH}/mi_versioned'

    for index, app in apps.iterrows():
        try:
            run_metric_all_versions(app["APPLICATION_NAME"], REPOS_BASE_PATH, output_path, start_date, end_date, run_mant_index)
        except Exception as e:
            logging.error(f"Error processing {app['APPLICATION_NAME']}: {e}")

def combine_results():
    combined_df = pd.DataFrame()
    apps = pd.read_csv(f"./datasets/applications.csv")
    for index, app in apps.iterrows():
        app_name = app["APPLICATION_NAME"]
        df = pd.read_csv(f"{OUTPUT_PATH}/mi_versioned/{app_name}.csv")
        df['APPLICATION_NAME'] = app_name
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    combined_output_path = f"{OUTPUT_PATH}/mi_versioned/apps_mi_versions.csv"
    combined_df.to_csv(combined_output_path, index=False)

def main():
    run_mi_verions_all_repos()
    #combine_results()

if __name__ == "__main__":
    main()
