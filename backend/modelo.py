"""Procesamiento + modelos: texto -> limpieza -> TF-IDF -> regresión logística -> categoría.

Hay tres clasificadores que trabajan en cadena:
  tipo  : Tutela / Derecho de petición / Demanda          (datos/dataset.csv)
  rama  : Derecho laboral / civil / administrativo         (Laboratorio 1: datos/rama_derecho.csv)
  tema  : asunto de la tutela (trabajo / mínimo vital /    (Laboratorio 2: datos/tutelas.csv)
          meritocracia). Solo se aplica si el tipo es Tutela.
"""
import json
import os
import re
import unicodedata
from pathlib import Path

import joblib

RAIZ = Path(__file__).resolve().parent.parent
DIR_MODELOS = Path(os.environ.get("GESTOR_MODELOS_DIR") or RAIZ / "backend")
RUTA_INFO = DIR_MODELOS / "modelos_info.json"

MODELOS = {
    "tipo": {"csv": "dataset.csv", "titulo": "Tipo de documento", "origen": "Gestor"},
    "rama": {"csv": "rama_derecho.csv", "titulo": "Rama del derecho", "origen": "Laboratorio 1"},
    "tema": {"csv": "tutelas.csv", "titulo": "Asunto de la tutela", "origen": "Laboratorio 2"},
}
# Por debajo de este umbral el documento queda "Requiere revisión humana".
UMBRAL_CONFIANZA = 0.5

STOPWORDS = set("""a al algo ante antes como con contra cual cuando de del desde donde dos el ella ellas ellos en entre
era es esa ese eso esta este esto estos fue ha han hasta hay la las le les lo los mas me mi muy ni no nos o otra otro
para pero por porque que quien se sea segun ser si sin sobre su sus tambien tiene un una uno unos y ya yo""".split())


class ErrorModelo(Exception):
    """El modelo no se puede cargar o aplicar."""


def preparar_texto(texto):
    t = texto.lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\[[a-z ]+\]", " ", t)          # marcas de anonimización
    t = re.sub(r"[^a-zñ\s]", " ", t)
    return " ".join(p for p in t.split() if p not in STOPWORDS and len(p) > 2)


def ruta_modelo(nombre):
    return DIR_MODELOS / f"modelo_{nombre}.joblib"


_cache = {}


def cargar(nombre):
    if nombre not in _cache:
        ruta = ruta_modelo(nombre)
        if not ruta.exists():
            raise ErrorModelo(f"No existe el modelo «{nombre}» ({ruta.name}). Ejecuta: python backend/entrenar.py")
        try:
            _cache[nombre] = joblib.load(ruta)
        except Exception as e:  # archivo corrupto o versión incompatible
            raise ErrorModelo(f"No se pudo cargar el modelo «{nombre}»: {e}") from e
    return _cache[nombre]


def cargar_todos():
    for nombre in MODELOS:
        cargar(nombre)


def info():
    return json.loads(RUTA_INFO.read_text(encoding="utf-8")) if RUTA_INFO.exists() else {}


def clasificar(nombre, texto):
    """Devuelve {categoria, confianza, probabilidades} del modelo indicado."""
    pipe = cargar(nombre)
    try:
        procesado = preparar_texto(texto)
        if not procesado:
            raise ErrorModelo("El texto no contiene palabras analizables.")
        probs = pipe.predict_proba([procesado])[0]
    except ErrorModelo:
        raise
    except Exception as e:
        raise ErrorModelo(f"Falló el procesamiento: {e}") from e
    dist = {c: float(p) for c, p in zip(pipe.classes_, probs)}
    mejor = max(dist, key=dist.get)
    return {"categoria": mejor, "confianza": dist[mejor], "probabilidades": dist}


def analizar(texto):
    """Cadena completa: tipo -> rama (siempre) -> tema (solo si es Tutela)."""
    tipo = clasificar("tipo", texto)
    rama = clasificar("rama", texto)
    tema = clasificar("tema", texto) if tipo["categoria"] == "Tutela" else None
    return tipo, rama, tema
