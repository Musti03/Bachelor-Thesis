import streamlit as st

def observability_section() -> str:
    st.subheader("2️⃣ Beobachtbarkeit des Ereigniseintritts")

    return st.radio(
        "Wie kann festgestellt werden, ob das Ereignis eingetreten ist?",
        options=[
            "Eindeutig feststellbar (ja / nein)",
            "Über Zählung / Anzahl von Vorfällen",
            "Mit Unsicherheit / Interpretationsspielraum",
            "Nicht eindeutig überprüfbar"
        ],
        help=(
            "Diese Angabe bestimmt, ob und wie ein Ereignisausgang "
            "später objektiv bewertet werden kann."
        )
    )
