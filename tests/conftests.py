import sys
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
