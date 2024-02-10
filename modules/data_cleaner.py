import pandas as pd
import datetime as dt
from datetime import datetime

tempo_days = pd.read_csv("data/tempo_days.csv", sep=";")


def missing_values(data: pd.DataFrame) -> pd.DataFrame:
    if data["Puissance"].isna().mean() < 0.1:
        data.fillna(0, inplace=True)
    return data


def split_hours(data: pd.DataFrame) -> pd.DataFrame:
    data['Horaire'] = pd.to_datetime(data['Horaire'])
    data['Puissance'] = pd.to_numeric(data['Puissance'])

    # Calcul la différence entre horaire n et n+1
    time_diff = data['Horaire'].diff()

    # True si la différence est égale à 30 minutes
    is_30 = (time_diff == pd.Timedelta(minutes=30))

    # DF des demie heures manquantes (et les puisances associées)
    new_rows = pd.DataFrame({
        'Horaire': data.loc[~is_30, 'Horaire'] - pd.Timedelta(minutes=30),
        'Puissance': data.loc[~is_30, 'Puissance'].values
    })

    new_df = pd.concat([new_rows, data], ignore_index=True)
    # Trier le DataFrame résultant par Horaire
    new_df = new_df.sort_values(by='Horaire').reset_index(drop=True)
    
    return new_df


def is_we(data: pd.DataFrame) -> bool:
    data["WE"] = False
    start_we = data["Horaire"].apply(lambda x: x.weekday()) >= 5
    stop_we = data["Horaire"].apply(lambda x: x.weekday()) <= 6
    data.loc[start_we & stop_we, "WE"] = True
    return data


def is_tempo(data: pd.DataFrame, tempo_blanc: list[datetime], tempo_rouge: list[datetime]) -> bool:
    is_white = data["Horaire"].apply(lambda x: x.date()).isin(tempo_blanc)
    is_red = data["Horaire"].apply(lambda x: x.date()).isin(tempo_rouge)

    data['tempo'] = 'bleu'
    data.loc[is_white, 'tempo'] = 'blanc'
    data.loc[is_red, 'tempo'] = 'rouge'
    return data


def set_hc(data: pd.DataFrame, hc_start: dt.time, hc_stop: dt.time, name_hc: str) -> pd.DataFrame:
    """Convertir les horaires de début et de fin en objets time
    """
    daytime = False
    horaire = data["Horaire"].apply(lambda x: x.time())
    
    if hc_start < hc_stop:
        daytime = True

    # Ajouter une colonne au DataFrame pour stocker les booléens
    data[name_hc] = 'HP'
    is_after_start = (hc_start <= horaire)
    is_before_stop = (horaire < hc_stop)
    
    if daytime == True:
        data.loc[is_after_start & is_before_stop, name_hc] = 'HC'
    else:
        data.loc[is_after_start | is_before_stop, name_hc] = 'HC'

    return data

def set_other(data: pd.DataFrame, horaires_other: dict[str, tuple[dt.time, dt.time]]) -> pd.DataFrame:
    """Convertir les horaires de début et de fin en objets time
    """
    daytime = False
    horaire = data["Horaire"].apply(lambda x: x.time())
    data['HC_other'] = 'HP'
    
    for key, value in horaires_other.items():
        hc_start = value[0]
        hc_stop = value[1]
        name_hc = key

        if hc_start < hc_stop:
            daytime = True

        is_after_start = (hc_start <= horaire)
        is_before_stop = (horaire < hc_stop)
        
        if daytime == True:
            data.loc[is_after_start & is_before_stop, 'HC_other'] = name_hc
        else:
            data.loc[is_after_start | is_before_stop, 'HC_other'] = name_hc

    return data


def data_completion(data: pd.DataFrame, horaires_dict: dict[str, tuple[dt.time, dt.time]], horaires_other: dict[str, tuple[dt.time, dt.time]]=None) -> pd.DataFrame:
    
    blanc = tempo_days['Tempo_blanc'].dropna()
    rouge = tempo_days['Tempo_rouge'].dropna()
    
    tempo_blanc = [datetime.strptime(date, "%d/%m/%Y").date().strftime("%d/%m") for date in blanc]
    tempo_rouge = [datetime.strptime(date, "%d/%m/%Y").date().strftime("%d/%m") for date in rouge]

    # Ajout des colonnes pour stocker les booléens
    data = is_we(data)
    data = is_tempo(data, tempo_blanc, tempo_rouge)
    
    for key, value in horaires_dict.items():
        data = set_hc(data, value[0], value[1], key)
    
    if horaires_other != None:
        data = set_other(data, horaires_other)
        
    return data