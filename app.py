import streamlit as st
from datetime import datetime, date
from models import RiskForecast
from storage import load_forecasts, save_forecast, save_all_forecasts
from scoring import brier_score, aggregate_brier_scores

# =================================================
# Seiteneinstellungen
# =================================================

st.set_page_config(
    page_title="Überprüfbare Risiko-Prognosen im CSRA",
    layout="wide"
)

st.title("Überprüfbare Risiko-Prognosen im CSRA")
st.caption(
    "Ich bin noch nicht ganz fertig, habe versucht erstmal mich auf das Prognoseformat zu konzentrieren"
)

# =================================================
# Neue Prognose anlegen
# =================================================

st.header("Neue Risiko-Prognose anlegen")

with st.form("create_forecast", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Metadaten (nicht bewertungsrelevant)")
        author = st.text_input("Urheber / Analyst *")
        team = st.text_input("Team (optional)")

        st.subheader("Prognose")
        event_description = st.text_input(
            "Beschreibung des prognostizierten Ereignisses *"
        )
        event_criteria = st.text_input(
            "Kriterien für den Ereigniseintritt *"
        )

    with col2:
        horizon_start = st.date_input(
            "Beginn Prognosehorizont",
            value=date.today()
        )
        horizon_end = st.date_input(
            "Ende Prognosehorizont *",
            value=date.today()
        )

        probability = st.slider(
            "Eintrittswahrscheinlichkeit",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01
        )

    rationale = st.text_area("Begründung (optional)")

    submitted = st.form_submit_button("Prognose speichern")

    if submitted:
        if not author or not event_description or not event_criteria:
            st.error("Bitte alle Pflichtfelder (*) ausfüllen.")
        elif horizon_end < horizon_start:
            st.error("Ende des Prognosehorizonts muss nach dem Beginn liegen.")
        else:
            forecast = RiskForecast.create(
                author=author,
                team=team if team else None,
                event_description=event_description,
                event_criteria=event_criteria,
                forecast_horizon_start=datetime.combine(
                    horizon_start, datetime.min.time()
                ),
                forecast_horizon_end=datetime.combine(
                    horizon_end, datetime.min.time()
                ),
                probability=probability,
                rationale=rationale if rationale else None
            )

            save_forecast(forecast)
            st.success("Prognose erfolgreich gespeichert.")

st.divider()

# =================================================
# Gespeicherte Prognosen
# =================================================

st.header("Gespeicherte Prognosen")

forecasts = load_forecasts()
now = datetime.utcnow()

expired = [
    f for f in forecasts
    if f.forecast_horizon_end < now and f.outcome is None
]

active = [
    f for f in forecasts
    if f.forecast_horizon_end >= now
]

# -------------------------------------------------
# Abgelaufene Prognosen – Überprüfung
# -------------------------------------------------

st.subheader("Abgelaufene Prognosen (zur Überprüfung)")

if not expired:
    st.info("Keine abgelaufenen Prognosen zur Überprüfung.")
else:
    for f in expired:
        with st.expander(f"Prognose {f.forecast_id}"):

            st.write(f"**Urheber:** {f.author}")
            if f.team:
                st.write(f"**Team:** {f.team}")

            st.write(f"**Ereignis:** {f.event_description}")
            st.write(f"**Kriterien:** {f.event_criteria}")
            st.write(
                f"**Prognosezeitraum:** "
                f"{f.forecast_horizon_start.date()} – {f.forecast_horizon_end.date()}"
            )
            st.write(f"**Wahrscheinlichkeit:** {f.probability}")

            outcome = st.radio(
                "Ist das Ereignis eingetreten?",
                options=[0, 1],
                format_func=lambda x: "Nein" if x == 0 else "Ja",
                key=f"outcome_{f.forecast_id}"
            )

            if st.button("Outcome speichern", key=f"save_{f.forecast_id}"):
                f.outcome = outcome
                f.evaluation_timestamp = datetime.utcnow()
                save_all_forecasts(forecasts)
                st.success("Outcome gespeichert.")

# -------------------------------------------------
# Aktive Prognosen
# -------------------------------------------------

st.subheader("Aktive Prognosen")

if not active:
    st.info("Keine aktiven Prognosen.")
else:
    for f in active:
        with st.expander(f"Prognose {f.forecast_id}"):

            st.write(f"**Urheber:** {f.author}")
            if f.team:
                st.write(f"**Team:** {f.team}")

            st.write(f"**Ereignis:** {f.event_description}")
            st.write(f"**Kriterien:** {f.event_criteria}")
            st.write(
                f"**Prognosehorizont:** "
                f"{f.forecast_horizon_start.date()} – {f.forecast_horizon_end.date()}"
            )
            st.write(f"**Wahrscheinlichkeit:** {f.probability}")
            st.info("Noch nicht überprüfbar – Prognosehorizont läuft.")

st.divider()

# =================================================
# Bewertung & Aggregation
# =================================================

st.header("Bewertung der Prognosen")

evaluated = [f for f in forecasts if f.outcome is not None]

if not evaluated:
    st.info("Noch keine bewerteten Prognosen vorhanden.")
else:
    for f in evaluated:
        bs = brier_score(f.probability, f.outcome)
        with st.expander(f"Prognose {f.forecast_id}"):
            st.write(f"**Urheber:** {f.author}")
            if f.team:
                st.write(f"**Team:** {f.team}")
            st.write(f"**Brier Score:** {bs:.3f}")

    st.subheader("Aggregierte Brier Scores (Durchschnitt)")

    st.markdown("**Nach Urheber:**")
    scores_author = aggregate_brier_scores(evaluated, by="author")
    for author, score in scores_author.items():
        st.write(f"- {author}: {score:.3f}")

    st.markdown("**Nach Team:**")
    scores_team = aggregate_brier_scores(evaluated, by="team")
    for team, score in scores_team.items():
        st.write(f"- {team}: {score:.3f}")
