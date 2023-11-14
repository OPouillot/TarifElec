import pandas as pd
import numpy as np

tarif_base = pd.read_csv('data/tarifs/tarif_base.csv', sep=";")
tarif_hc = pd.read_csv('data/tarifs/tarif_hc.csv', sep=";")
tarif_tempo = pd.read_csv('data/tarifs/tarif_tempo.csv', sep=";")
tarif_zen_we = pd.read_csv('data/tarifs/tarif_zen_we.csv', sep=";")
tarif_zen_we_hc =  pd.read_csv('data/tarifs/tarif_zen_we_hc.csv', sep=";")


def abo_cost(data: pd.DataFrame, abo: float) -> float:
    month_start = data["Horaire"].iloc[0].month
    month_stop = data["Horaire"].iloc[-1].month
    year_start = data["Horaire"].iloc[0].year
    year_stop = data["Horaire"].iloc[-1].year

    cost = abo * ((year_stop - year_start) * 12 + month_stop - month_start)
    return cost


def prix_base(data: pd.DataFrame, puissance: int, tarif: pd.DataFrame) -> pd.DataFrame:
    tarif_kwh = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix'].iloc[0] / 100
    data["cost_base"] = (data['Puissance'] / 2000) * tarif_kwh
    
    return data


def prix_hc(data: pd.DataFrame, puissance: int,  tarif: pd.DataFrame) -> pd.DataFrame:
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'].iloc[0] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'].iloc[0] / 100
    
    data['cost_hc'] = np.where((data['HC_EDF'] == 'HC'),
                               (data['Puissance'] / 2000) * tarif_kwh_hc,
                               (data['Puissance'] / 2000) * tarif_kwh_hp)
    
    return data


def prix_tempo(data: pd.DataFrame, puissance: int,  tarif: pd.DataFrame) -> pd.DataFrame:
    
    tarif_kwh_hp_bleu = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Bleu HP'].iloc[0] / 100
    tarif_kwh_hc_bleu = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Bleu HC'].iloc[0] / 100
    tarif_kwh_hp_blanc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Blanc HP'].iloc[0] / 100
    tarif_kwh_hc_blanc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Blanc HC'].iloc[0] / 100
    tarif_kwh_hp_rouge = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Rouge HP'].iloc[0] / 100
    tarif_kwh_hc_rouge = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Rouge HC'].iloc[0] / 100
    
    conditions = [
        (~(data['HC_tempo'] == 'HC') & (data['tempo'] == "bleu")),
        ((data['HC_tempo'] == 'HC') & (data['tempo'] == "bleu")),
        (~(data['HC_tempo'] == 'HC') & (data['tempo'] == "blanc")),
        ((data['HC_tempo'] == 'HC') & (data['tempo'] == "blanc")),
        (~(data['HC_tempo'] == 'HC') & (data['tempo'] == "rouge")),
        ((data['HC_tempo'] == 'HC') & (data['tempo'] == "rouge")),
    ]
    tarifs = [
        (data['Puissance'] / 2000) * tarif_kwh_hp_bleu,
        (data['Puissance'] / 2000) * tarif_kwh_hc_bleu,
        (data['Puissance'] / 2000) * tarif_kwh_hp_blanc,
        (data['Puissance'] / 2000) * tarif_kwh_hc_blanc,
        (data['Puissance'] / 2000) * tarif_kwh_hp_rouge,
        (data['Puissance'] / 2000) * tarif_kwh_hc_rouge,
    ]
    data['cost_tempo'] = np.select(conditions, tarifs, default=0)

    return data


def prix_zen_we(data: pd.DataFrame, puissance: int,  tarif: pd.DataFrame) -> pd.DataFrame:
    
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'].iloc[0] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'].iloc[0] / 100
    
    data['cost_zen_we'] = np.where(data['WE'],
                                   (data['Puissance'] / 2000) * tarif_kwh_hc,
                                   (data['Puissance'] / 2000) * tarif_kwh_hp)
    
    return data


def prix_zen_we_hc(data: pd.DataFrame, puissance: int,  tarif: pd.DataFrame) -> pd.DataFrame:
    
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'].iloc[0] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'].iloc[0] / 100
    
    data['cost_zen_we_hc'] = np.where(data['WE'] | (data['HC_EDF'] == 'HC'),
                                      (data['Puissance'] / 2000) * tarif_kwh_hc,
                                      (data['Puissance'] / 2000) * tarif_kwh_hp)
    return data


def prix_other_supplier(data: pd.DataFrame, tarifs_other: dict, horaires_other: dict, is_we=False) -> pd.DataFrame:
    conditions = []
    tarifs = []
    keys = list(horaires_other.keys())

    if is_we:
        # Condition WE
        conditions.append(data['WE'])
        tarifs.append((data['Puissance'] / 2000) * (tarifs_other['WE']/100))
        # Condition HCs
        for key, value in horaires_other.items():
            conditions.append((data['HC_other'] == key) & ~data['WE'])
            tarifs.append((data['Puissance'] / 2000) * (tarifs_other[key]/100))
    else:
        # Condition HCs
        for key, value in horaires_other.items():
            conditions.append((data['HC_other'] == key))
            tarifs.append((data['Puissance'] / 2000) * (tarifs_other[key]/100))

    conditions.append((data['HC_other'] == 'HP'))
    tarifs.append((data['Puissance'] / 2000) * (tarifs_other['HP']/100))

    data['cost_other'] = np.select(conditions, tarifs, default=0)
    
    return data


def calc_costs(data:pd.DataFrame, puissance: int, tarifs_other: dict=None, horaires_other: dict=dict(), is_we: bool=False) -> pd.DataFrame:
    
    data = prix_base(data, puissance, tarif_base)
    data = prix_hc(data, puissance, tarif_hc)
    data = prix_tempo(data, puissance, tarif_tempo)
    data = prix_zen_we(data, puissance, tarif_zen_we)
    data = prix_zen_we_hc(data, puissance, tarif_zen_we_hc)
    if tarifs_other:
        data = prix_other_supplier(data, tarifs_other, horaires_other, is_we)

    abo_base = abo_cost(data, tarif_base.loc[tarif_base['Puissance Souscrite'] == puissance, 'Abonnement'].iloc[0])
    abo_hc = abo_cost(data, tarif_hc.loc[tarif_hc['Puissance Souscrite'] == puissance, 'Abonnement'].iloc[0])
    abo_tempo = abo_cost(data, tarif_tempo.loc[tarif_tempo['Puissance Souscrite'] == puissance, 'Abonnement'].iloc[0])
    abo_zen_we = abo_cost(data, tarif_zen_we.loc[tarif_zen_we['Puissance Souscrite'] == puissance, 'Abonnement'].iloc[0])
    abo_zen_we_hc = abo_cost(data, tarif_zen_we_hc.loc[tarif_zen_we_hc['Puissance Souscrite'] == puissance, 'Abonnement'].iloc[0])

    cost = pd.DataFrame(columns=["Abonnement", "Coût Total"])
    cost = pd.DataFrame(data=[("EDF - Base", data["cost_base"].sum() + abo_base),
                              ("EDF - Heures Creuses", data["cost_hc"].sum() + abo_hc),
                              ("EDF - Tempo", data["cost_tempo"].sum() + abo_tempo),
                              ("EDF - Zen Week-end", data["cost_zen_we"].sum() + abo_zen_we),
                              ("EDF - Zen Week-end + Heures Creuses", data["cost_zen_we_hc"].sum() + abo_zen_we_hc)],
                        columns=["Abonnement", "Coût Total"])
    
    if tarifs_other:
        abo_other_tot = abo_cost(data, tarifs_other["abo"])
        cost_other = pd.DataFrame(data = [('Autre fournisseur', data["cost_other"].sum() + abo_other_tot)], columns=["Abonnement", "Coût Total"])
        cost = pd.concat([cost, cost_other], ignore_index=True)

    return cost
