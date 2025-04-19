from git import Repo
import datetime
import re
import logging
import pandas as pd

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPOS_BASE_PATH = "../repos"

def checkout_master_fetch_and_reset(repo_path):
    repo = Repo(repo_path)
    logging.info(f"Checkout master of {repo_path}")
    repo.git.checkout("master")
    logging.info(f"Fetch {repo_path}")
    repo.git.fetch()
    logging.info(f"Reset {repo_path}")
    repo.git.reset("--hard", "origin/master")


def get_repo_id(repo_name):
    return "-".join(word[:2] for word in repo_name.split("-"))

def get_first_releasable_tag_date(repo_name):
    repo_path = f"{REPOS_BASE_PATH}/{repo_name}"
    repo = Repo(repo_path)
    # Define timezone for Argentina (UTC-3)
    argentina_tz = datetime.timezone(datetime.timedelta(hours=-3))

    # Define a regex pattern for releasable version tags (e.g., 1.2.3, 1.2.3-rc-1, 1.2.3-hotfix-2)
    releasable_tag_pattern = re.compile(r'^\d+\.\d+\.\d+(-rc-\d+|-hotfix-\d+)?$')

    releasable_tags = [
        tag.commit.committed_datetime.astimezone(argentina_tz).replace(tzinfo=None)
        for tag in repo.tags
        if releasable_tag_pattern.match(tag.name)
    ]

    return min(releasable_tags) if releasable_tags else None


def get_releasable_tags(repo, start_date, end_date):
    # Define timezone for Argentina (UTC-3)
    argentina_tz = datetime.timezone(datetime.timedelta(hours=-3))

    # Define a regex pattern for releasable version tags (e.g., 1.2.3, 1.2.3-rc-1, 1.2.3-hotfix-2)
    releasable_tag_pattern = re.compile(r'^\d+\.\d+\.\d+(-rc-\d+|-hotfix-\d+)?$')

    # Filter tags based on the releasable version pattern and the commit date
    releasable_tags = []
    for tag in repo.tags:
        tag_date = tag.commit.committed_datetime.astimezone(argentina_tz).replace(tzinfo=None)

        if (
            releasable_tag_pattern.match(tag.name) and
            tag_date > start_date and
            tag_date < end_date
        ):
            releasable_tags.append({
                "name": tag.name,
                "commit": tag.commit.hexsha,
                "date": tag_date
            })

    # Sort tags by commit date
    releasable_tags.sort(key=lambda x: x["date"])

    return releasable_tags

def run_metric_all_versions(repo_name, output_path, start_date, end_date, metric_metod):
    repo_path = f"{REPOS_BASE_PATH}/{repo_name}"

    logging.info(f"Running {metric_metod} for repository {repo_name} from {start_date} to {end_date}")

    # Abrir el repositorio
    repo = Repo(repo_path)

    tags = get_releasable_tags(repo, start_date, end_date)

    # Crear un DataFrame vacío para acumular los resultados
    results_df = pd.DataFrame()
    
    # get length of tags
    len_tags = len(tags)

    for index, tag in enumerate(tags):
        logging.info(f"Running Metric for tag {tag['name']} on {tag['date']} ({index+1}/{len_tags})")
        
        repo.git.checkout(tag['name'])
        
        tag_results = metric_metod(repo_path)
        tag_results["tag_name"] = tag["name"]
        tag_results["tag_date"] = tag["date"]
        results_df = pd.concat([results_df, tag_results], ignore_index=True)

    # Guardar el DataFrame final a un archivo CSV
    final_output_path = f"{output_path}/{repo_name}.csv"
    results_df.to_csv(final_output_path, index=False)
    logging.info(f"Combined results saved to {final_output_path}")