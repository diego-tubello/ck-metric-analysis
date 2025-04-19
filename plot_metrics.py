import pandas as pd
from plot_ck import plot_ck_over_time
from plot_deploys import plot_deploys_over_time
import matplotlib.pyplot as plt

def main():
    # Configurar el tamaño de fuente global
    plt.rcParams.update({'font.size': 14})
    date_range = pd.date_range(start='2023-01-01', end='2025-02-28', freq='M')
    plot_ck_over_time(date_range)
    plot_deploys_over_time(date_range)


if __name__ == "__main__":
    main()
