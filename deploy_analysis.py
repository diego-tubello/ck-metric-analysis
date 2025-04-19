import pandas as pd

def count_monthly_deploys():
    df = pd.read_csv(f"./datasets/apps_deploys.csv")

    # Filtrar solo los deploys con SERVICE_CRITICALLITY != 'low'
    df = df[df['SERVICE_CRITICALLITY'] != 'low']
    
    # Crear una columna para el año/mes de DEPLOY_DATE
    df['YEAR_MONTH'] = pd.to_datetime(df['DEPLOY_DATE'].str[:7], format='%Y-%m')

    # Crear una tabla pivote para contar los despliegues por APPLICATION_NAME, YEAR_MONTH y DEPLOY_STATUS
    pivot_df = df.pivot_table(index=['APPLICATION_NAME', 'YEAR_MONTH'], columns='DEPLOY_STATUS', aggfunc='size', fill_value=0).reset_index()

    # Renombrar las columnas para mayor claridad
    pivot_df.columns.name = None
    pivot_df = pivot_df.rename(columns={'rollbacked': 'ROLLBACKED_COUNT', 'finished': 'FINISHED_COUNT'})

    # Agregar una columna con el total de despliegues
    pivot_df['TOTAL_COUNT'] = pivot_df['ROLLBACKED_COUNT'] + pivot_df['FINISHED_COUNT']

    # Calcular la tasa de rollback
    pivot_df['ROLLBACK_RATIO'] = (pivot_df['ROLLBACKED_COUNT'] / pivot_df['TOTAL_COUNT']).round(2)

    pivot_df.to_csv(f"./datasets/apps_deploys_monthly.csv", index=False)    


def main():
    count_monthly_deploys()


if __name__ == "__main__":
    main()