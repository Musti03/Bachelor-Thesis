import streamlit as st
from datetime import date

def time_horizon_section():
    st.subheader("3️⃣ Zeitlicher Bezug der Prognose")

    start = st.date_input("Beginn des Prognosezeitraums", value=date.today())
    end = st.date_input("Ende des Prognosezeitraums")

    return start, end
