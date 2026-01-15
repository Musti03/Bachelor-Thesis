FROM python:3.11-slim

# Verhindert unnötige Python-Caches
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY . .

# Streamlit-Port
EXPOSE 8501

# Start des Demonstrators
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
