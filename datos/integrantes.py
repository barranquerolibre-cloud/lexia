"""Integrantes del equipo (fuente única: datos/integrantes.json). Lo usan los generadores de datos y el backend."""
import json
from pathlib import Path

RUTA = Path(__file__).resolve().parent / "integrantes.json"


def cargar():
    return json.loads(RUTA.read_text(encoding="utf-8"))


def revisor(i):
    """Reparto rotativo: el fragmento número i de cada categoría se asigna a un integrante distinto."""
    nombres = cargar()
    return nombres[i % len(nombres)]
