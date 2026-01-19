import streamlit as st

def statement_type_section() -> str:
    st.subheader("1️⃣ Art der Prognoseaussage")

    return st.radio(
        "Welche Art von Aussage möchten Sie treffen?",
        options=[
            "Ereignis tritt ein / tritt nicht ein",
            "Ereignis tritt mehrfach auf (Häufigkeit)",
            "Ereignis möglicherweise / unklar",
            "Qualitative Einschätzung (Trend, Reifegrad)"
        ],
        help=(
            "Diese Auswahl bestimmt, wie die Prognose später "
            "formal klassifiziert und bewertet werden kann."
        )
    )
