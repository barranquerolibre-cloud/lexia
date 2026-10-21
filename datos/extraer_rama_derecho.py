"""Extrae los 120 textos del cuaderno del Laboratorio 1 a datos/rama_derecho.csv.

Lee las celdas que definen las listas `laboral`, `civil` y `administrativo` en
Laboratorio1_Clasificacion_Juridica.ipynb, para que la aplicación use exactamente el mismo corpus del Lab 1.
"""
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CUADERNO = RAIZ / "Laboratorio1_Clasificacion_Juridica.ipynb"
ETIQUETAS = {"laboral": "Derecho laboral", "civil": "Derecho civil", "administrativo": "Derecho administrativo"}


def main():
    celdas = json.loads(CUADERNO.read_text(encoding="utf-8"))["cells"]
    espacio = {}
    for c in celdas:
        codigo = "".join(c["source"])
        if c["cell_type"] == "code" and any(f"{n} = [" in codigo for n in ETIQUETAS):
            exec(codigo, espacio)  # solo asigna listas de texto; el cuaderno es del propio equipo
    filas, n = [], 0
    for nombre, etiqueta in ETIQUETAS.items():
        for texto in espacio[nombre]:
            n += 1
            filas.append({"id": n, "texto": texto, "categoria": etiqueta, "origen": "cuaderno_lab1",
                          "revisado_por": "Equipo (Laboratorio 1)"})
    destino = Path(__file__).parent / "rama_derecho.csv"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "texto", "categoria", "origen", "revisado_por"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} textos -> {destino}")


if __name__ == "__main__":
    main()
