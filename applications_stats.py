import datetime
import pandas as pd
import re
from dateutil.relativedelta import relativedelta
from repo_utils import get_repo_id, get_first_releasable_tag_date

release_version_pattern = re.compile(r'^\d+\.\d+\.\d+$')

def get_first_release_dates():
    # Suponiendo que df es tu DataFrame con las columnas: class, tag_name, tag_date, APPLICATION_NAME
    df = pd.read_csv(f"./datasets/applications.csv")
    df['first_release_date'] = df['APPLICATION_NAME'].apply(get_first_releasable_tag_date)
    df['first_release_date'] = df['first_release_date'].dt.strftime('%Y-%m-%d')
    df.to_csv('./datasets/applications_first_release_date.csv', index=False)   

# Calcular la diferencia en meses entre el primer y el último release
def diff_months(d1, d2):
    rd = relativedelta(d2, d1)
    return rd.years * 12 + rd.months + 1  # +1 para incluir el mes de inicio

def get_group(row, period_length):
    if row['active_months'] >= period_length:
        if row['period_activity'] < 1.0:
            return 1 # Repositorios antiguos con baja actividad
        else: 
            return 2 # Repositorios antiguos con media/alta actividad
    else:
        return 3 # repositoprios nuevos

def get_stats():
    period_start_date = datetime.datetime(2023, 1, 1)
    period_end_date = datetime.datetime(2025, 2, 28)
    period_length = diff_months(period_start_date, period_end_date)

    # Suponiendo que df es tu DataFrame con las columnas: class, tag_name, tag_date, APPLICATION_NAME
    df = pd.read_csv(f"./datasets/apps_ck_versions.csv")
    df['tag_date'] = pd.to_datetime(df['tag_date'])

    first_release_dates = pd.read_csv(f"./datasets/applications_first_release_date.csv")
    first_release_dates['first_release_date'] = pd.to_datetime(first_release_dates['first_release_date'])

    # Filtrar las versiones que coincidan con el patrón de versión release
    release_versions = df[df['tag_name'].apply(lambda x: bool(release_version_pattern.match(x)))]

    # Eliminar duplicados basados en APPLICATION_NAME y tag_name
    release_versions_unique = release_versions.drop_duplicates(subset=['APPLICATION_NAME', 'tag_name'])

    # Obtener la cantidad de clases de la versión más reciente para cada aplicación
    latest_versions = df.sort_values('tag_date').drop_duplicates('APPLICATION_NAME', keep='last')
    latest_versions_class_counts = df[df['tag_date'].isin(latest_versions['tag_date'])].groupby('APPLICATION_NAME')['class'].nunique().reset_index()
    latest_versions_class_counts = latest_versions_class_counts.rename(columns={'class': 'class_count'})

    # Contar el número de versiones release únicas para cada aplicación
    period_release_counts = release_versions_unique.groupby('APPLICATION_NAME').size().reset_index(name='period_release_count')

    # Combinar los resultados en un solo DataFrame
    result = pd.merge(first_release_dates, latest_versions_class_counts, on='APPLICATION_NAME')
    result = pd.merge(result, period_release_counts, on='APPLICATION_NAME')
   
    result['active_months'] = result.apply(
        lambda row: diff_months(row['first_release_date'], period_end_date), 
        axis=1)
    
    result['period_activity'] = result.apply(
        lambda row: round(row['period_release_count'] / min(row['active_months'], period_length), 2), 
        axis=1)
    
    result['group'] = result.apply(
        lambda row: get_group(row, period_length), 
        axis=1)

    result['first_release_date'] = result['first_release_date'].dt.strftime('%Y-%m-%d')
    result['repo_id'] = result['APPLICATION_NAME'].apply(get_repo_id)

    result = result[[
        'APPLICATION_NAME', 
        'repo_id', 'class_count', 'first_release_date', 'active_months', 'period_release_count', 'period_activity', 'group']]

    result.to_csv('./datasets/applications_stats.csv', index=False)  # Guardar el resultado en un archivo CSV

def main():
    #get_first_release_dates()
    get_stats()


if __name__ == "__main__":
    main()