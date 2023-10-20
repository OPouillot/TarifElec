
def abo_cost(data, abo):
    month_start = data["Horaire"].iloc[0].month
    month_stop = data["Horaire"].iloc[-1].month
    year_start = data["Horaire"].iloc[0].year
    year_stop = data["Horaire"].iloc[-1].year

    cost = abo * ((year_stop - year_start) * 12 + month_stop - month_start)
    return cost

def prix_base(data, puissance, tarif):
    abo = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Abonnement']
    abo_tot = abo_cost(data, abo)
    
    tarif_kwh = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix'] / 100
    sum_kwh = data['Puissance'].sum() / 2000
    
    prix_base = abo_tot + tarif_kwh * sum_kwh
    
    return {'Abonnement': 'Base', 'Coût Total': round(prix_base, 2)}

def prix_hc(data, puissance,  tarif):
    abo = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Abonnement']
    abo_tot = abo_cost(data, abo)
    
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'] / 100
    
    sum_kwh_hp = data['Puissance'].loc[data['HC_EDF'] == False].sum() / 2000
    sum_kwh_hc = data['Puissance'].loc[data['HC_EDF'] == True].sum() / 2000
    
    prix_hc = abo_tot + tarif_kwh_hp * sum_kwh_hp + tarif_kwh_hc * sum_kwh_hc
    
    return {'Abonnement': 'Heures Creuses', 'Coût Total': round(prix_hc, 2)}

def prix_tempo(data, puissance,  tarif):
    abo = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Abonnement']
    abo_tot = abo_cost(data, abo)
    
    tarif_kwh_hp_bleu = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Bleu HP'] / 100
    tarif_kwh_hc_bleu = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Bleu HC'] / 100
    tarif_kwh_hp_blanc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Blanc HP'] / 100
    tarif_kwh_hc_blanc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Blanc HC'] / 100
    tarif_kwh_hp_rouge = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Rouge HP'] / 100
    tarif_kwh_hc_rouge = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix Rouge HC'] / 100
    
    sum_kwh_hp_bleu = data['Puissance'].loc[(data['HC_tempo'] == False)
                                            & (data['tempo_blanc'] == False)
                                            & (data['tempo_rouge'] == False)].sum() / 2000
    sum_kwh_hc_bleu = data['Puissance'].loc[(data['HC_tempo'] == True)
                                            & (data['tempo_blanc'] == False)
                                            & (data['tempo_rouge'] == False)].sum() / 2000
    sum_kwh_hp_blanc = data['Puissance'].loc[(data['HC_tempo'] == False)
                                            & (data['tempo_blanc'] == True)].sum() / 2000
    sum_kwh_hc_blanc = data['Puissance'].loc[(data['HC_tempo'] == True)
                                            & (data['tempo_blanc'] == True)].sum() / 2000
    sum_kwh_hp_rouge = data['Puissance'].loc[(data['HC_tempo'] == False)
                                            & (data['tempo_rouge'] == True)].sum() / 2000
    sum_kwh_hc_rouge = data['Puissance'].loc[(data['HC_tempo'] == True)
                                            & (data['tempo_rouge'] == True)].sum() / 2000
    
    prix_tempo = (abo_tot + 
                  tarif_kwh_hp_bleu * sum_kwh_hp_bleu + 
                  tarif_kwh_hc_bleu * sum_kwh_hc_bleu +
                  tarif_kwh_hp_blanc * sum_kwh_hp_blanc + 
                  tarif_kwh_hc_blanc * sum_kwh_hc_blanc +
                  tarif_kwh_hp_rouge * sum_kwh_hp_rouge + 
                  tarif_kwh_hc_rouge * sum_kwh_hc_rouge)
    
    return {'Abonnement': 'Tempo', 'Coût Total': round(prix_tempo, 2)}

def prix_zen_we(data, puissance, tarif):
    abo = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Abonnement']
    abo_tot = abo_cost(data, abo)
    
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'] / 100
    
    sum_kwh_hp = data['Puissance'].loc[data['WE'] == False].sum() / 2000
    sum_kwh_hc = data['Puissance'].loc[data['WE'] == True].sum() / 2000
    
    prix_zen_we = abo_tot + tarif_kwh_hp * sum_kwh_hp + tarif_kwh_hc * sum_kwh_hc
    
    return {'Abonnement': 'Zen Week-end', 'Coût Total': round(prix_zen_we, 2)}

def prix_zen_we_hc(data, puissance, tarif):
    abo = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Abonnement']
    abo_tot = abo_cost(data, abo)
    
    tarif_kwh_hp = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HP'] / 100
    tarif_kwh_hc = tarif.loc[tarif['Puissance Souscrite'] == puissance, 'Prix HC'] / 100
    
    sum_kwh_hp = data['Puissance'].loc[(data['WE'] == False) & (data['HC_EDF'] == False)].sum() / 2000
    sum_kwh_hc = data['Puissance'].loc[(data['WE'] == True) | (data['HC_EDF'] == True)].sum() / 2000
    
    prix_zen_we_hc = abo_tot + tarif_kwh_hp * sum_kwh_hp + tarif_kwh_hc * sum_kwh_hc
    
    return {'Abonnement': 'Zen Week-end Heures Creuses', 'Coût Total': round(prix_zen_we_hc, 2)}

def prix_other_supplier(data, tarifs_other, horaires_other, is_we=False):
    sum_kwh = dict()
    keys = list(horaires_other.keys())
    abo_tot = abo_cost(data, tarifs_other["abo"])
    
    for key, value in horaires_other.items():
        sum_kwh[key] = data['Puissance'].loc[data[key] == True].sum() / 2000
    
    if is_we:
        sum_kwh["WE"] = data['Puissance'].loc[(data["WE"] == True) &
                                              (data[keys[0]] == False)].sum() / 2000
        keys.append("WE")
        sum_kwh["HP"] = data['Puissance'].loc[~data[keys].any(axis=1)].sum() / 2000
        
        prix = abo_tot + tarifs_other["HP"]/100 * sum_kwh["HP"] + tarifs_other["WE"]/100 * sum_kwh["WE"]
    else:
        sum_kwh["HP"] = data['Puissance'].loc[~data[keys].any(axis=1)].sum() / 2000
        
        prix = abo_tot + tarifs_other["HP"]/100 * sum_kwh["HP"]
    
    for key, value in horaires_other.items():
        prix = prix + (tarifs_other[key]/100 * sum_kwh[key])
    
    return {'Abonnement': 'Autre Fournisseur', 'Coût Total': round(prix, 2)}

