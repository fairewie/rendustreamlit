import streamlit as st
import pandas as pd

from function import DataBase


database = DataBase(name_database='yugioh')
nom_table = 'carte_yugioh'
dates_uniques = database.select_distinct_dates(nom_table)
selected_date = st.selectbox("Sélectionnez une date", dates_uniques)
st.write(f"Vous avez sélectionné la date : {selected_date}")


data_for_selected_date = database.select_data_for_date(nom_table, selected_date)

df = pd.DataFrame(data_for_selected_date)
st.write(df)