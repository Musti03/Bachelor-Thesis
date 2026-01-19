import streamlit as st

def probability_origin_section():
    st.subheader("4️⃣ Herkunft der Eintrittswahrscheinlichkeit")

    origin = st.radio(
        "Wie wird die Eintrittswahrscheinlichkeit bestimmt?",
        options=[
            "Direkte Schätzung durch Experten",
            "Abgeleitet aus vorhandenen Daten / Statistiken",
            "Kombination mehrerer Faktoren (z. B. Vorfragen)",
            "Keine explizite Wahrscheinlichkeit angegeben"
        ],
        help=(
            "Die Herkunft der Wahrscheinlichkeit wird dokumentiert, "
            "aber nicht automatisch bewertet oder korrigiert."
        )
    )

    probability = None
    if origin != "Keine explizite Wahrscheinlichkeit angegeben":
        probability = st.slider(
            "Geschätzte Eintrittswahrscheinlichkeit",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=0.5
        )

    return origin, probability
