import os
import pandas as pd
import numpy as np
import seaborn as sns  
import matplotlib.pyplot as plt
import datetime as dt
from datetime import datetime
import streamlit as st
from modules import data_cleaner, cost_calc

# INPUTSa
hc_start = "20:30"
hc_stop = "04:30"
puissance = 6
# SCROLLING MENU (with "other supplier" choice revealing other inputs)
offre_actu = "Zen Week-end Heures Creuses"

# INPUTS ?? Not sure
hc_tempo_start = "22:00"
hc_tempo_stop = "06:00"

# To be build from input data
horaires_dict = {
    'HC_EDF': (hc_start, hc_stop),
    'HC_tempo': (hc_tempo_start, hc_tempo_stop),
    'HC1': ("20:30", "04:30")
}

# if scrolling menu == "other supplier"
horaires_other = {
    'HC1': ("20:30", "04:30")
}
tarifs_other = {
    'abo': 13.03,
    'HP': 26.83,
    'HC1': 18.81,
    'WE': 18.81
}


file = pd.read_csv('./data/Enedis_Conso_Heure_20221221-20230820_02198263279373.csv', sep=";")
tarif_base = pd.read_csv('./data/tarifs/tarif_base.csv', sep=";")
tarif_hc = pd.read_csv('./data/tarifs/tarif_hc.csv', sep=";")
tarif_tempo = pd.read_csv('./data/tarifs/tarif_tempo.csv', sep=";")
tarif_zen_we = pd.read_csv('./data/tarifs/tarif_zen_we.csv', sep=";")
tarif_zen_we_hc =  pd.read_csv('./data/tarifs/tarif_zen_we_hc.csv', sep=";")

data = file.iloc[2:,0:2]
data.rename(columns={'Identifiant PRM': "Horaire", "Type de donnees": "Puissance"}, inplace=True)
data.reset_index(drop=True)

data = data_cleaner.missing_values(data)
data = data_cleaner.split_hours(data)
data = data_cleaner.data_completion(data, horaires_dict)

costs = pd.DataFrame(columns=['Abonnement', 'Coût Total'])
costs = pd.concat([costs,
                   pd.DataFrame(cost_calc.prix_base(data, puissance, tarif_base)),
                   pd.DataFrame(cost_calc.prix_hc(data, puissance, tarif_hc)),
                   pd.DataFrame(cost_calc.prix_tempo(data, puissance, tarif_tempo)),
                   pd.DataFrame(cost_calc.prix_zen_we(data, puissance, tarif_zen_we)),
                   pd.DataFrame(cost_calc.prix_zen_we_hc(data, puissance, tarif_zen_we_hc)),
                   pd.DataFrame([cost_calc.prix_other_supplier(data, tarifs_other, horaires_other, is_we=True)])], ignore_index=True)

print(costs)