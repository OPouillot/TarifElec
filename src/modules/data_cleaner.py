import pandas as pd
from datetime import datetime

tempo_days = pd.read_csv("../data/tempo_days.csv", sep=";")


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


def is_we(data):
    if 5 <= data.weekday() <= 6:
        return True
    else:
        return False


def is_tempo_white(data, tempo_blanc):
    if data.date() in tempo_blanc:
        return True
    else:
        return False


def is_tempo_red(data, tempo_rouge):
    if data.date() in tempo_rouge:
        return True
    else:
        return False


def set_hc(data, hc_start, hc_stop, name_hc):
    """Convertir les horaires de début et de fin en objets time
    """
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


def data_completion(data, horaires_dict):
    
    blanc = tempo_days['Tempo_blanc'].dropna()
    rouge = tempo_days['Tempo_rouge'].dropna()
    
    tempo_blanc = [datetime.strptime(date, "%d/%m/%Y").date() for date in blanc]
    tempo_rouge = [datetime.strptime(date, "%d/%m/%Y").date() for date in rouge]

    # Ajout des colonnes pour stocker les booléens
    data["WE"] = False
    data['tempo_blanc'] = False
    data['tempo_rouge'] = False
    
    # Parcourir chaque ligne du DataFrame
    for index, row in data.iterrows():
        data.loc[index, 'WE'] = is_we(row['Horaire'])
        data.loc[index, 'tempo_blanc'] = is_tempo_white(row['Horaire'], tempo_blanc)
        data.loc[index, 'tempo_rouge'] = is_tempo_red(row['Horaire'], tempo_rouge)
    for key, value in horaires_dict.items():
        data = set_hc(data, value[0], value[1], key)
        
    return data