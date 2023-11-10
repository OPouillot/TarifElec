import pandas as pd
import datetime as dt
from PIL import Image
import plotly.express as px
import streamlit as st
from modules import data_cleaner, cost_calc

# Initialisation de la configuration de la page
st.set_page_config(
    page_title="TarifElec - Quel abonnement pour payer moins cher ma facture d'électricité",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_months(data: pd.DataFrame) -> str:
    return pd.to_datetime(data["Horaire"], utc=True).dt.strftime('%B %Y').unique()

def submission():
    st.session_state.form_sub = True
    st.session_state.calc_done = False


def main():

    if "form_sub" not in st.session_state:
        st.session_state.form_sub = False
    if "calc_done" not in st.session_state:
        st.session_state.calc_done = False
    
    image = Image.open('data/icon.png')
    col1, col2 = st.columns([1,4])
    with col1:
        st.image(image, use_column_width="auto")
    with col2:
        st.title("TarifElec - Optimiser son abonnement d'électricité !")
    
    tarif_base = pd.read_csv('data/tarifs/tarif_base.csv', sep=";")
    tarif_hc = pd.read_csv('data/tarifs/tarif_hc.csv', sep=";")
    tarif_tempo = pd.read_csv('data/tarifs/tarif_tempo.csv', sep=";")
    tarif_zen_we = pd.read_csv('data/tarifs/tarif_zen_we.csv', sep=";")
    tarif_zen_we_hc =  pd.read_csv('data/tarifs/tarif_zen_we_hc.csv', sep=";")

    with st.sidebar:
        offre_actu = st.selectbox("Quelle est votre offre actuelle?",
                                  ("EDF - Base", 
                                   "EDF - Heures Creuses", 
                                   "EDF - Tempo",
                                   "EDF - Zen Week-end", 
                                   "EDF - Zen Week-end + Heures Creuses",
                                   "Autre fournisseur"))
        other_bool = (offre_actu == "Autre fournisseur")
        if other_bool:
            hc_bool = st.checkbox("Une option Heures creuses ?")
            we_bool = st.checkbox("Une option Week-end ?")

        # Formulaire pour infos abo client
        with st.form("client_infos"):
            loaded_file = st.file_uploader('Chargez votre fichier "Consommation par heure" Enedis (format csv)', type=['csv'])
            st.write("Heures creuses dans votre commune ?")
            col1, col2 = st.columns(2)
            with col1:
                hc_start = st.time_input("Début HC", dt.time(20, 30))
            with col2:
                hc_stop = st.time_input("Fin HC", dt.time(4,30))
            puissance = st.number_input(label="Puissance souscrite (kVA)", value=6)
            
            if other_bool:
                hc_prices = dict()
                hc_hours = dict()
                if hc_bool:
                    c1, c2 = st.columns(2)
                    with c1:
                        other_abo = st.number_input("Prix de votre abonnement")
                    with c2:
                        other_hp = st.number_input("Prix Heures Pleines (cts€/kWh)")
                    st.write("Ne remplir que les informations Heures Creuses utiles !")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        hc_prices['HC1'] = st.number_input("Prix HC1 (cts€/kWh)")
                        hc_prices['HC2'] = st.number_input("Prix HC2 (cts€/kWh)")
                        hc_prices['Hc3'] = st.number_input("Prix HC3 (cts€/kWh)")
                    with c2:
                        hc_hours['HC1_start'] = st.time_input("Début HC1", dt.time(00, 00))
                        hc_hours['HC2_start'] = st.time_input("Début HC2", dt.time(00, 00))
                        hc_hours['HC3_start'] = st.time_input("Début HC3", dt.time(00, 00))
                    with c3:
                        hc_hours['HC1_stop'] = st.time_input("Fin HC1", dt.time(00, 00))
                        hc_hours['HC2_stop'] = st.time_input("Fin HC2", dt.time(00, 00))
                        hc_hours['HC3_stop'] = st.time_input("Fin HC3", dt.time(00, 00))
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        other_abo = st.number_input("Prix de votre abonnement")
                    with c2:
                        other_hp = st.number_input("Prix du kWh (cts€/kWh)")
                if we_bool:
                    other_we = st.number_input("Prix Week-End (cts€/kWh)")
            st.write("")
            st.write("")
            submit = st.form_submit_button("Charger données", on_click=submission)

    # Si formulaire envoyé
    if st.session_state.form_sub and not st.session_state.calc_done:
        with st.spinner('Calcul en cours ...'):
            
            # To be build from input data
            horaires_dict = {
                'HC_EDF': (hc_start, hc_stop),
                'HC_tempo': (dt.time(22, 00), dt.time(6, 00)), # SHOULD BE ENV VARIABLES for modification
            }

            if other_bool:
                tarifs_other = dict()
                horaires_other = dict()
                for key, value in hc_prices.items():
                    if value != 0:
                        tarifs_other[key] = value
                if we_bool:
                    tarifs_other['WE'] = other_we
                tarifs_other['HP'] = other_hp
                tarifs_other['abo'] = other_abo

                for key, value in hc_prices.items():
                    if value != 0:
                        if (hc_hours[key+'_start'] != dt.time(00,00) and hc_hours[key+'_stop'] != dt.time(00,00)):
                            horaires_other[key] = (hc_hours[key+'_start'], hc_hours[key+'_stop'])
                        else: 
                            st.warning("Il y a une erreur dans le renseignement des données ", key)
                horaires_dict.update(horaires_other)


            file = pd.read_csv(loaded_file, sep=";")

            data = file.iloc[2:,0:2]
            data.rename(columns={'Identifiant PRM': "Horaire", "Type de donnees": "Puissance"}, inplace=True)
            data.reset_index(drop=True)
            data = data_cleaner.missing_values(data)
            data = data_cleaner.split_hours(data)
            data = data_cleaner.data_completion(data, horaires_dict)

            date_start = data.iloc[0,0].strftime("%d/%m/%Y")
            date_stop = data.iloc[-1,0].strftime("%d/%m/%Y")

            costs = pd.DataFrame(data=[cost_calc.prix_base(data, puissance, tarif_base),
                                        cost_calc.prix_hc(data, puissance, tarif_hc),
                                        cost_calc.prix_tempo(data, puissance, tarif_tempo),
                                        cost_calc.prix_zen_we(data, puissance, tarif_zen_we),
                                        cost_calc.prix_zen_we_hc(data, puissance, tarif_zen_we_hc)],
                                columns=['Abonnement', 'Coût Total'])
            if other_bool:
                costs = pd.concat([costs,pd.DataFrame([cost_calc.prix_other_supplier(data, tarifs_other, horaires_other, is_we=we_bool)])], ignore_index=True)
            
            reference_cost = costs.loc[costs["Abonnement"] == offre_actu, "Coût Total"].values[0]
            costs['Pourcentage'] = ((costs['Coût Total'] - reference_cost) / reference_cost) * 100
            st.session_state.cost = costs
            st.session_state.data = data
            st.session_state.calc_done = True

            st.rerun()

    elif st.session_state.calc_done:
        tab1, tab2 = st.tabs(["Comparatifs", "Ma consommation"])

        with tab1:
            costs = st.session_state.cost
            data = st.session_state.data
            date_start = data.iloc[0,0].strftime("%d/%m/%Y")
            date_stop = data.iloc[-1,0].strftime("%d/%m/%Y")
            data
            costs

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"Estimation coût élec sur la période du {date_start} au {date_stop}")
                fig_costs = px.bar(costs, x='Abonnement', y='Coût Total')
                st.plotly_chart(fig_costs, use_container_width=True)
            with col2:
                st.subheader("Ecart par rapport à votre abonnement (en %)")
                fig_prct = px.bar(costs, x='Abonnement', y='Pourcentage')
                st.plotly_chart(fig_prct, use_container_width=True)
        
        with tab2:
            # Faire une selectbox avec les mois dispos dans les data user
            months = get_months(data)
            month_selected = st.selectbox("Choisissez le mois à observer", months)

            day_power = data.groupby(pd.to_datetime(data['Horaire'], utc=True).dt.date)['Puissance'].sum() / 2000
            day_power = pd.DataFrame(day_power)
            day_power.reset_index(inplace=True)
            max_power = day_power["Puissance"].max()
            month_power = day_power.loc[pd.to_datetime(day_power["Horaire"], utc=True).dt.strftime('%B %Y') == month_selected]
            fig_month = px.bar(month_power, x="Horaire", y="Puissance", title=f"Consommation {month_selected}", range_y=[0,max_power])
            st.plotly_chart(fig_month, use_container_width=True)

    else:
        st.write("")
        st.header("Comment ça marche ?", divider="orange")
        st.subheader("Votre abonnement en électricité est-il adapté à votre rythme de vie ? ")
        st.write("Pour répondre à cette question, l'idée est simple :\n\n"
                 "Déterminer combien vous aurait couté votre électricité selon les différents abonnements proposés par EDF, à partir de vos données de consommations passées.\n\n"
                 "Comparaisons entre votre abonnement (même d'un autre fournisseur) et 5 abonnement EDF :\n"
                 "- **Tarif Réglementé** (tarif bleu de base)\n- **Tarif Heure creuse** (tarif bleu avec 8h/jours moins cher, généralement la nuit)\n"
                 "- **Tarifs Tempo** (Un abonnement qui varie en fonction des tensions du réseau : électricité moins cher 343jours/ans, et 22 jours rouges 3x plus cher)\n"
                 "- **Tarif Zen Week-End** (une offre de marché à prix réduit le week-end)\n"
                 "- **Tarif Zen Week-End + Heures creuses** (offre de marché à prix réduit le week-end et 8h/jours)")
        
        st.header("Comment récupérer ses données Enedis ?", divider="orange")
        st.subheader("Suivez les instructions ci-dessous :")
        st.write('''1. Rendez-vous sur le site officiel [Enedis](https://mon-compte-client.enedis.fr/).\n'''
                 '''2. Connectez-vous à votre compte ou créez-le.  \n:warning: Si vous n'avez pas de compteur linky associé, je vous guide [juste en dessous !](#linky)\n'''
                 '''3. Allez sur l'onglet "Suivre mes mesures" et descendez jusqu'à voir le bouton "Télécharger mes données".\n'''
                 '''4. Dans "Type de données", choisissez "Consommation horaire", et sélectionnez la période que vous souhaitez.  \n'''
                 ''':warning: Si l'option "Consommation horaire" est grisée, rendez-vous d'abord dans l'onglet "Gérer l'accès à mes données" et activez l'enregistrement, ainsi que la collecte de la consommation horaire.\n\n'''
                 ''':heavy_check_mark: Quelques minutes plus tard (ou heures, selon la volonté d'Enedis :face_with_rolling_eyes:), votre fichier de consommation est disponible '''
                 '''dans vos téléchargements.''')
        
        st.header("Associer son compteur linky", anchor="linky", divider="orange")


if __name__ == '__main__':
    main()
