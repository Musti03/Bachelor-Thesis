import streamlit as st
from datetime import datetime, date

from csra_forecast.models import RiskForecast
from csra_forecast.storage import load_forecasts, save_forecast, save_all_forecasts
from csra_forecast.scoring import is_brier_applicable, brier_score, aggregate_brier_scores
from csra_forecast.probability import derive_probability_from_factors


# ==================================================
# Page setup
# ==================================================
st.set_page_config(page_title="Überprüfbare CSRA-Prognosen", layout="wide")
st.title("Überprüfbare Risiko-Prognosen im CSRA")

st.info(
    "Dieses Tool implementiert das in der Thesis entwickelte Prognoseformat.\n\n"
    "Ziel ist nicht sofortige Bewertung, sondern **strukturierte Überprüfbarkeit**, "
    "Transformation und spätere Evaluation."
)


# ==================================================
# Session-State Initialisierung
# ==================================================
def init_state():
    defaults = {
        "forecast_name": "",
        "author": "",
        "team": "",
        "event_description": "",
        "event_criteria": "",
        "rationale": "",

        "statement_type": "Ereignis tritt ein / tritt nicht ein",
        "observability": "Eindeutig feststellbar (ja / nein)",

        "evaluation_mode": "FIXED",
        "horizon_start": date.today(),
        "horizon_end": date.today(),

        "prob_source": "Expertenschätzung",
        "probability": 0.5,

        "threshold_definition": "",

        # Wizard
        "wiz_base_rate": 0.1,
        "wiz_exposure": 0.5,
        "wiz_controls": 0.5,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ==================================================
# Mapping (Thesis-Logik!)
# ==================================================
STATEMENT_TO_PT = {
    "Ereignis tritt ein / tritt nicht ein": "PT1",
    "Ereignis tritt mehrfach auf (Häufigkeit)": "PT2",
    "Ereignis möglicherweise / unklar": "PT3",
    "Qualitative Einschätzung (Trend, Reifegrad)": "PT4",
}

OBS_TO_O = {
    "Eindeutig feststellbar (ja / nein)": "O1",
    "Über Zählung / Anzahl von Vorfällen": "O2",
    "Mit Unsicherheit / Interpretationsspielraum": "O3",
    "Nicht eindeutig überprüfbar": "O4",
}

EVAL_MODE_MAP = {
    "Fester Zeitraum (Start/Ende)": "FIXED",
    "Offen (Start bekannt, Ende offen)": "OPEN",
    "Ereignisgetrieben (Trigger)": "EVENT",
    "Unbekannt / nicht spezifiziert": "UNKNOWN",
}


# ==================================================
# Eingabe UI
# ==================================================
st.header("Neue Risiko-Prognose anlegen")

col1, col2 = st.columns(2)

# ---------------- Metadaten ----------------
with col1:
    st.subheader("Metadaten")
    st.session_state["forecast_name"] = st.text_input("Prognose-Name (optional)", st.session_state["forecast_name"])
    st.session_state["author"] = st.text_input("Urheber / Analyst *", st.session_state["author"])
    st.session_state["team"] = st.text_input("Team (optional)", st.session_state["team"])

    st.subheader("Strukturierte Vorfragen")
    st.session_state["statement_type"] = st.radio(
        "Welche Art von Aussage?",
        list(STATEMENT_TO_PT.keys()),
    )

    st.session_state["observability"] = st.radio(
        "Wie wird der Eintritt festgestellt?",
        list(OBS_TO_O.keys()),
    )

    derived_pt = STATEMENT_TO_PT[st.session_state["statement_type"]]
    derived_o = OBS_TO_O[st.session_state["observability"]]

    st.caption(f"➡️ Abgeleitet: **{derived_pt} / {derived_o}**")


# ---------------- Inhalt ----------------
with col2:
    st.subheader("Prognoseinhalt")
    st.session_state["event_description"] = st.text_input(
        "Beschreibung des Ereignisses *",
        st.session_state["event_description"],
    )
    st.session_state["event_criteria"] = st.text_input(
        "Kriterien für den Eintritt *",
        st.session_state["event_criteria"],
    )

    # -------- Evaluation / Horizont --------
    st.subheader("Evaluation / Prognosehorizont")
    eval_label = st.selectbox("Evaluationsmodus", list(EVAL_MODE_MAP.keys()))
    eval_mode = EVAL_MODE_MAP[eval_label]

    horizon_start_dt = None
    horizon_end_dt = None

    if eval_mode == "FIXED":
        st.session_state["horizon_start"] = st.date_input("Beginn", st.session_state["horizon_start"])
        st.session_state["horizon_end"] = st.date_input("Ende", st.session_state["horizon_end"])
        horizon_start_dt = datetime.combine(st.session_state["horizon_start"], datetime.min.time())
        horizon_end_dt = datetime.combine(st.session_state["horizon_end"], datetime.min.time())

    elif eval_mode in ("OPEN", "EVENT"):
        st.session_state["horizon_start"] = st.date_input("Start (optional)", st.session_state["horizon_start"])
        horizon_start_dt = datetime.combine(st.session_state["horizon_start"], datetime.min.time())
        horizon_end_dt = None
        st.info("Ende bewusst offen – Evaluation später.")

    else:
        st.warning("Kein zeitlicher Horizont angegeben → nur strukturell dokumentiert.")


    # -------- Wahrscheinlichkeit --------
    st.subheader("Eintrittswahrscheinlichkeit")
    prob_source = st.radio(
        "Herkunft",
        [
            "Expertenschätzung",
            "Abgeleitet aus Daten",
            "Automatisch abgeleitet (Wizard)",
            "Keine explizite Wahrscheinlichkeit",
        ],
    )

    probability = None
    derivation = None

    if prob_source == "Automatisch abgeleitet (Wizard)":
        st.markdown("**Ableitung über Faktoren:**")
        st.session_state["wiz_base_rate"] = st.slider("Basisrate", 0.0, 1.0, st.session_state["wiz_base_rate"])
        st.session_state["wiz_exposure"] = st.slider("Exposition", 0.0, 1.0, st.session_state["wiz_exposure"])
        st.session_state["wiz_controls"] = st.slider("Kontrollstärke", 0.0, 1.0, st.session_state["wiz_controls"])

        derivation = derive_probability_from_factors(
            base_rate=st.session_state["wiz_base_rate"],
            exposure=st.session_state["wiz_exposure"],
            control_strength=st.session_state["wiz_controls"],
        )
        probability = derivation["result_probability"]
        st.success(f"Abgeleitete Wahrscheinlichkeit: {probability:.2f}")

    elif prob_source != "Keine explizite Wahrscheinlichkeit" and derived_pt != "PT4":
        probability = st.slider("Wahrscheinlichkeit", 0.0, 1.0, st.session_state["probability"])

st.session_state["rationale"] = st.text_area("Begründung / Kontext", st.session_state["rationale"])


# ==================================================
# Save
# ==================================================
if st.button("Prognose speichern"):
    try:
        forecast = RiskForecast.create(
            forecast_type=derived_pt,
            outcome_class=derived_o,
            event_description=st.session_state["event_description"],
            event_criteria=st.session_state["event_criteria"],
            evaluation_mode=eval_mode,
            forecast_horizon_start=horizon_start_dt,
            forecast_horizon_end=horizon_end_dt,
            probability=probability,
            probability_derivation=derivation,
            forecast_name=st.session_state["forecast_name"],
            author=st.session_state["author"],
            team=st.session_state["team"],
            rationale=st.session_state["rationale"],
        )
        save_forecast(forecast)
        st.success("Prognose gespeichert.")
    except Exception as e:
        st.error(str(e))


# ==================================================
# Anzeige & Evaluation
# ==================================================
st.divider()
st.header("Gespeicherte Prognosen")

forecasts = load_forecasts()
now = datetime.utcnow()

for f in forecasts:
    with st.expander(f.forecast_name or f.forecast_id):
        st.write(f"**Typ:** {f.forecast_type} | **Outcome:** {f.outcome_class}")
        st.write(f"**Ereignis:** {f.event_description}")
        st.write(f"**Wahrscheinlichkeit:** {f.probability}")

        if f.outcome is None:
            outcome = st.radio("Eingetreten?", [0, 1], key=f"out_{f.forecast_id}")
            if st.button("Outcome speichern", key=f"save_{f.forecast_id}"):
                f.set_outcome(outcome)
                save_all_forecasts(forecasts)

        if is_brier_applicable(f):
            st.write(f"**Brier Score:** {brier_score(f.probability, f.outcome):.3f}")
        else:
            st.info("Nicht quantitativ bewertbar.")


# ==================================================
# Aggregation
# ==================================================
st.divider()
st.header("Aggregierte Auswertung")
scores = aggregate_brier_scores(forecasts)
for k, v in scores.items():
    st.write(f"{k}: {v:.3f}")
