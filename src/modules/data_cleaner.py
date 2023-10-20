import pandas as pd
import datetime as dt
from datetime import datetime

tempo_days = pd.read_csv("./data/tempo_days.csv", sep=";")


def missing_values(data):
    if data["Puissance"].isna().mean() < 0.1:
        data.fillna(0, inplace=True)
    return data

def split_hours(data):
    new_rows = []
    all_horaires = pd.to_datetime(data['Horaire'])
    
    for index, row in data.iterrows():
        horaire = pd.to_datetime(row['Horaire'])
        puissance = int(row['Puissance'])
        last_half_hour = horaire - pd.Timedelta(minutes=30)
        
        # Si le relevé est à l'heure et que le précédent n'est pas 30 minutes avant
        if horaire.minute == 0 and last_half_hour not in all_horaires.values:
            new_rows.append({'Horaire': last_half_hour, 'Puissance': puissance})
            new_rows.append({'Horaire': horaire, 'Puissance': puissance})
        else:  # Si le relevé est déjà à la demi-heure
            new_rows.append({'Horaire': horaire, 'Puissance': puissance})

    new_df = pd.DataFrame(new_rows)
    return new_df

def convert_string_to_time(str):
    if len(str) < 4:
        return dt.time(hour=int(str[0]), minute=int(str[1:3]))
    else:
        return dt.time(hour=int(str[0:2]), minute=int(str[3:5]))

def set_we(data):
    data["WE"] = False
    
    # Parcourir chaque ligne du DataFrame
    for index, row in data.iterrows():
        horaire = row['Horaire'].weekday()

        # Comparer l'horaire avec les horaires de début et de fin
        if 5 <= horaire <= 6:
            data.loc[index, 'WE'] = True
            
    return data

def set_hc(data, hc_start, hc_stop, name_hc):
    """Convertir les horaires de début et de fin en objets time
    """
    hc_start = convert_string_to_time(hc_start)
    hc_stop = convert_string_to_time(hc_stop)
    daytime = False
    
    if hc_start < hc_stop:
        daytime = True

    # Ajouter une colonne au DataFrame pour stocker les booléens
    data[name_hc] = False

    # Parcourir chaque ligne du DataFrame
    for index, row in data.iterrows():
        horaire = row['Horaire'].time()

        # Si heure creuse jour
        if daytime == True:
            # Comparer l'horaire avec les horaires de début et de fin
            if hc_start <= horaire and horaire < hc_stop:
                data.loc[index, name_hc] = True
                
        # Si heure creuse nuit (entre j et j+1)
        else:
            # Comparer l'horaire avec les horaires de début et de fin
            if hc_start <= horaire or horaire < hc_stop:
                data.loc[index, name_hc] = True

    return data

def set_blue_white_red(data):
    blanc = tempo_days['Tempo_blanc'].dropna()
    rouge = tempo_days['Tempo_rouge'].dropna()
    
    tempo_blanc = [datetime.strptime(date, "%d/%m/%Y").date() for date in blanc]
    tempo_rouge = [datetime.strptime(date, "%d/%m/%Y").date() for date in rouge]
    
    # Ajouter une colonne au DataFrame pour stocker les booléens
    data['tempo_blanc'] = False
    data['tempo_rouge'] = False
    
    # Parcourir chaque ligne du DataFrame
    for index, row in data.iterrows():
        horaire = row['Horaire'].date()
        
        if horaire in tempo_blanc:
            data.loc[index, 'tempo_blanc'] = True
        elif horaire in tempo_rouge:
            data.loc[index, 'tempo_rouge'] = True
    
    return data

def data_completion(data, horaires_dict):
    data = set_we(data)
    data = set_blue_white_red(data)
    for key, value in horaires_dict.items():
        data = set_hc(data, value[0], value[1], key)
        
    return data