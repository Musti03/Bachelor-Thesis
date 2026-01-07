# Prototyp: Überprüfbare Risiko-Prognosen im CSRA

Dieser Prototyp dient als **technischer Demonstrator** für das im Rahmen der
Bachelorarbeit entwickelte **maschinenlesbare Prognoseformat** zur
Überprüfbarkeit von Risiko-Prognosen im Cyber Security Risk Assessment (CSRA).

---

## Zielsetzung

Ziel des Prototyps ist es zu zeigen, dass das konzeptionell entwickelte
Prognoseformat

- technisch umsetzbar ist,
- maschinell verarbeitet werden kann,
- eine klare Trennung zwischen Prognose, Prognosehorizont und
  Ereignisausgang ermöglicht,
- sowie eine nachträgliche quantitative Bewertung von Prognosen erlaubt.

Die Implementierung dient ausschließlich der **Illustration des
entwickelten Konzepts**. Sie erhebt keinen Anspruch auf Vollständigkeit,
Skalierbarkeit, Produktionsreife oder den Einsatz in sicherheitskritischen
Produktivumgebungen.

---

## Funktionaler Umfang

Der Prototyp unterstützt exemplarisch:

- die strukturierte Erfassung von Risiko-Prognosen über eine grafische
  Benutzeroberfläche,
- die explizite zeitliche Fixierung von Prognosen mittels Prognosehorizont,
- die getrennte Erfassung des tatsächlichen Ereignisausgangs (Outcome) nach
  Ablauf des Prognosehorizonts,
- die quantitative Bewertung einzelner Prognosen mittels Brier Score,
- eine einfache aggregierte Auswertung von Bewertungsergebnissen,
- die reproduzierbare Ausführung der Anwendung in einer containerisierten
  Umgebung.

---

## Technischer Überblick

- **Programmiersprache:** Python  
- **Grafische Benutzeroberfläche:** Streamlit  
- **Datenhaltung:** lokale JSON-Datei  
- **Bewertungsmetrik:** Brier Score (binäre Ereignisse)  
- **Ausführung:** Docker (Containerisierung)

---

## Projektstruktur

```text
.
├── app.py              # Streamlit-GUI (Erfassung, Überprüfung, Bewertung)
├── models.py           # Datenmodell (RiskForecast)
├── storage.py          # Persistenz & Historisierung
├── scoring.py          # Bewertungslogik (Brier Score)
├── forecasts.json      # Persistente Speicherung (automatisch erzeugt)
├── requirements.txt    # Python-Abhängigkeiten
├── Dockerfile          # Container-Setup
└── README.md           # Projektdokumentation
