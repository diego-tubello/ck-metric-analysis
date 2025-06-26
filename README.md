# CK Metric Analysis

Este repositorio contiene un conjunto de herramientas para analizar métricas CK (Chidamber & Kemerer) en proyectos Java y su relación con la tasa de rollbacks en despliegues.

## Descripción

El proyecto realiza análisis de las siguientes métricas CK:
- WMC (Weighted Methods per Class)
- DIT (Depth of Inheritance Tree)
- NOC (Number of Children)
- CBO (Coupling Between Objects)
- RFC (Response For a Class)
- LCOM (Lack of Cohesion in Methods)

## Estructura del Proyecto

- `datasets/`: Contiene los archivos CSV con datos de métricas y despliegues
  - `apps_ck_versions.csv`: Métricas CK por versión de cada aplicación
  - `apps_deploys.csv`: Datos de despliegues y rollbacks
  - `correlations/`: Resultados de análisis de correlaciones

- `notebooks/`: Jupyter notebooks para análisis y transformación de datos
  - `convert_data.ipynb`: Conversión de datos crudos
  - `correlate_ck_versions.ipynb`: Análisis de correlaciones
  - `transform_corr_data.ipynb`: Transformación de datos de correlación

- `plots/`: Gráficos y visualizaciones generadas
  - `correlations/`: Gráficos de correlaciones
  - `histograms/`: Distribución de métricas

## Scripts Principales

- `ck_analysis.py`: Análisis principal de métricas CK
- `correlations.py`: Cálculo de correlaciones entre métricas y rollbacks
- `plot_ck.py`: Generación de gráficos para métricas CK
- `plot_correlations.py`: Visualización de correlaciones
- `plot_metrics.py`: Gráficos generales de métricas

## Requisitos

Las dependencias del proyecto se encuentran en `requirements.txt`.

## Uso

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar análisis de correlaciones:
```bash
python correlations.py
```

3. Generar visualizaciones:
```bash
python plot_correlations.py
```

## Herramientas Utilizadas

- CK Tool (v0.7.1): Para extraer métricas CK
- Python 3.13
- Pandas: Para análisis de datos
- Matplotlib/Seaborn: Para visualizaciones
