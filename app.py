import streamlit as st
from datetime import datetime, date

from models import RiskForecast
from storage import load_forecasts, save_forecast, save_all_forecasts
from scoring import aggregate_brier_scores, is_brier_applicable, brier_score
from classification import classify_forecast

# --------------------------------
# Seiteneinstellungen
# --------------------------------

st.set_page_config(
    page_title="Überprüfbare Risiko-Prognosen im CSRA",
    layout="wide"
)

st.title("Überprüfbare Risiko-Prognosen im CSRA")

st.info(
    "Dieses System demonstriert ein überprüfbares Prognoseformat "
    "für Cyber Security Risk Assessment.\n\n"
    "Prognosetypen und Outcome-Klassen werden nicht frei gewählt, "
    "sondern aus strukturierten Vorfragen abgeleitet."
)

# --------------------------------
# Neue Prognose
# --------------------------------

st.header("Neue Risiko-Prognose anlegen")

with st.form("create_forecast", clear_on_submit=True):

    col1, col2 = st.columns(2)

    # ---------- Metadaten ----------
    with col1:
        st.subheader("Metadaten")
        forecast_name = st.text_input("Prognose-Name (optional)")
        author = st.text_input("Urheber / Analyst *")
        team = st.text_input("Team (optional)")

    # ---------- Vorfragen ----------
    st.subheader("Strukturierte Vorfragen")

    statement_type = st.radio(
        "1️⃣ Welche Art von Aussage möchten Sie treffen?",
        [
            "Ereignis tritt ein / tritt nicht ein",
            "Ereignis tritt mehrfach auf (Häufigkeit)",
            "Ereignis möglicherweise / unklar",
            "Qualitative Einschätzung (Trend, Reifegrad)"
        ]
    )

    observability = st.radio(
        "2️⃣ Wie kann der Ereigniseintritt festgestellt werden?",
        [
            "Eindeutig feststellbar (ja / nein)",
            "Über Zählung / Anzahl von Vorfällen",
            "Mit Unsicherheit / Interpretationsspielraum",
            "Nicht eindeutig überprüfbar"
        ]
    )

    # ---------- Ableitung ----------
    forecast_type, outcome_class = classify_forecast(
        statement_type=statement_type,
        observability=observability
    )

    st.caption(
        f"➡️ Abgeleiteter Prognosetyp: **{forecast_type}**, "
        f"Outcome-Klasse: **{outcome_class}**"
    )

    # ---------- Prognoseinhalt ----------
    with col2:
        st.subheader("Prognoseinhalt")

        event_description = st.text_input(
            "Beschreibung des prognostizierten Ereignisses *"
        )

        event_criteria = st.text_input(
            "Kriterien für den Ereigniseintritt *"
        )

        horizon_start = st.date_input(
            "Beginn Prognosehorizont",
            value=date.today()
        )

        horizon_end = st.date_input(
            "Ende Prognosehorizont *",
            value=date.today()
        )

        probability_origin = st.radio(
            "3️⃣ Herkunft der Eintrittswahrscheinlichkeit",
            [
                "Experteneinschätzung",
                "Abgeleitet aus Daten",
                "Kombination mehrerer Faktoren",
                "Keine explizite Wahrscheinlichkeit"
            ]
        )

        probability = None
        if probability_origin != "Keine explizite Wahrscheinlichkeit":
            probability = st.slider(
                "Geschätzte Eintrittswahrscheinlichkeit",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                value=0.5
            )

        threshold_definition = None
        if outcome_class == "O2":
            threshold_definition = st.text_input(
                "Schwellendefinition (z. B. ≥ 3 Vorfälle)",
                help="Erforderlich für häufigkeitsbasierte Aussagen"
            )

    rationale = st.text_area("Begründung / Kontext (optional)")

    submitted = st.form_submit_button("Prognose speichern")

    if submitted:
        if not author or not event_description or not event_criteria:
            st.error("Bitte alle Pflichtfelder ausfüllen.")
        elif horizon_end < horizon_start:
            st.error("Ende des Prognosehorizonts muss nach dem Beginn liegen.")
        else:
            forecast = RiskForecast.create(
                forecast_type=forecast_type,
                outcome_class=outcome_class,
                event_description=event_description,
                event_criteria=event_criteria,
                forecast_horizon_start=datetime.combine(
                    horizon_start, datetime.min.time()
                ),
                forecast_horizon_end=datetime.combine(
                    horizon_end, datetime.min.time()
                ),
                probability=probability if probability is not None else 0.0,
                forecast_name=forecast_name,
                author=author,
                team=team,
                rationale=rationale,
                threshold_definition=threshold_definition
            )

            save_forecast(forecast)
            st.success("Prognose gespeichert.")

st.divider()

# --------------------------------
# Prognosen anzeigen & bewerten
# --------------------------------

st.header("Gespeicherte Prognosen")

forecasts = load_forecasts()
now = datetime.utcnow()

for f in forecasts:
    with st.expander(f"Prognose: {f.forecast_name or f.forecast_id}"):

        st.write(f"**Prognosetyp:** {f.forecast_type}")
        st.write(f"**Outcome-Klasse:** {f.outcome_class}")
        st.write(f"**Vergleichsebene:** {f.comparison_level}")
        st.write(f"**Ereignis:** {f.event_description}")
        st.write(
            f"**Zeitraum:** "
            f"{f.forecast_horizon_start.date()} – {f.forecast_horizon_end.date()}"
        )
        st.write(f"**Wahrscheinlichkeit:** {f.probability}")

        if f.outcome is None and f.forecast_horizon_end < now:
            outcome = st.radio(
                "Ist das Ereignis eingetreten?",
                [0, 1],
                format_func=lambda x: "Nein" if x == 0 else "Ja",
                key=f"outcome_{f.forecast_id}"
            )

            if st.button("Outcome speichern", key=f"save_{f.forecast_id}"):
                f.outcome = outcome
                f.evaluation_timestamp = datetime.utcnow()
                f.comparison_level = "E3"
                save_all_forecasts(forecasts)
                st.success("Outcome gespeichert – Prognose ist nun bewertbar.")

        if is_brier_applicable(f):
            st.write(
                f"**Brier Score:** "
                f"{brier_score(f.probability, f.outcome):.3f}"
            )
        else:
            st.info("Diese Prognose ist (noch) nicht quantitativ bewertbar.")

st.divider()

# --------------------------------
# Aggregierte Auswertung
# --------------------------------

st.header("Aggregierte Auswertung (Demonstration)")

scores_author = aggregate_brier_scores(forecasts, by="author")
if not scores_author:
    st.info("Noch keine aggregierbaren Prognosen.")
else:
    for author, score in scores_author.items():
        st.write(f"- **{author}**: {score:.3f}")
