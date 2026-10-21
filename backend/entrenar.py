"""Entrena los tres clasificadores con los CSV de datos/ y guarda backend/modelo_*.joblib (+ métricas)."""
import json
import sys
from datetime import datetime

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from modelo import DIR_MODELOS, MODELOS, RAIZ, RUTA_INFO, preparar_texto, ruta_modelo


def nuevo_pipe():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("lr", LogisticRegression(C=10, max_iter=2000)),
    ])


def entrenar(nombre, cfg):
    df = pd.read_csv(RAIZ / "datos" / cfg["csv"], encoding="utf-8")
    df["x"] = df["texto"].apply(preparar_texto)
    cats = sorted(df["categoria"].unique())
    X_tr, X_te, y_tr, y_te = train_test_split(df["x"], df["categoria"], test_size=0.25,
                                              random_state=42, stratify=df["categoria"])
    pred = nuevo_pipe().fit(X_tr, y_tr).predict(X_te)
    cv = cross_val_score(nuevo_pipe(), df["x"], df["categoria"], cv=StratifiedKFold(5, shuffle=True, random_state=42))
    informe = classification_report(y_te, pred, output_dict=True, zero_division=0)
    # Modelo final: se reentrena con todo el corpus para usarlo en la aplicación.
    joblib.dump(nuevo_pipe().fit(df["x"], df["categoria"]), ruta_modelo(nombre))
    return {
        "titulo": cfg["titulo"], "origen_laboratorio": cfg["origen"], "archivo_datos": cfg["csv"],
        "origen_datos": sorted(df["origen"].unique().tolist()), "muestras": int(len(df)), "categorias": cats,
        "por_categoria": {k: int(v) for k, v in df["categoria"].value_counts().items()},
        "muestras_prueba": int(len(y_te)), "exactitud_prueba": round(float(accuracy_score(y_te, pred)), 3),
        "exactitud_cv_media": round(float(cv.mean()), 3), "exactitud_cv_desv": round(float(cv.std()), 3),
        "matriz_confusion": confusion_matrix(y_te, pred, labels=cats).tolist(),
        "f1_por_categoria": {c: round(informe[c]["f1-score"], 3) for c in cats},
    }


def main():
    DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    resultado = {"entrenado": datetime.now().isoformat(timespec="seconds"),
                 "modelo": "TF-IDF (1-2 gramas) + Regresión logística", "modelos": {}}
    for nombre, cfg in MODELOS.items():
        resultado["modelos"][nombre] = entrenar(nombre, cfg)
        m = resultado["modelos"][nombre]
        print(f"{nombre:5s} {m['titulo']:22s} {m['muestras']:>3d} textos | prueba {m['exactitud_prueba']:.0%} "
              f"(n={m['muestras_prueba']}) | validación cruzada {m['exactitud_cv_media']:.0%} ± {m['exactitud_cv_desv']:.0%}")
    RUTA_INFO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
