"""Backend del gestor de tutelas, derechos de petición y demandas.

Ejecutar:  python backend/app.py   ->  http://127.0.0.1:5000
"""
import json
import logging
import os
import time
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory

import db
import modelo
from ficha import generar_pdf
from extraer import MAX_CHARS, SOPORTADOS, ErrorArchivo, extraer_texto

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
RUTA_LOG = Path(os.environ.get("GESTOR_LOG") or RAIZ / "evidencia" / "registro_backend.log")
RUTA_LOG.parent.mkdir(exist_ok=True)

RAMAS = ["Derecho laboral", "Derecho civil", "Derecho administrativo"]            # Laboratorio 1
TEMAS = ["Derecho al trabajo", "Mínimo vital", "Meritocracia"]                       # Laboratorio 2
def _integrantes():
    ruta = RAIZ / "datos" / "integrantes.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []


INTEGRANTES = _integrantes()
MIN_CHARS = 40
MAX_ARCHIVOS = 10
CATEGORIAS = {
    "Tutela": "Acción para proteger derechos fundamentales ante una vulneración actual o inminente.",
    "Derecho de petición": "Solicitud respetuosa a una autoridad o particular para obtener información, copias o una decisión.",
    "Demanda": "Escrito que inicia un proceso judicial con partes, hechos, pretensiones y pruebas.",
}

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

log = logging.getLogger("gestor")
log.setLevel(logging.INFO)
_h = logging.FileHandler(RUTA_LOG, encoding="utf-8")
_h.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
log.addHandler(_h)


def error(mensaje, codigo, estado):
    g.detalle = f"ERROR {codigo}: {mensaje}"
    return jsonify({"error": mensaje, "codigo": codigo}), estado


@app.before_request
def _inicio():
    g.t0 = time.perf_counter()
    g.detalle = ""


@app.after_request
def _registro(resp):
    if request.path.startswith("/api/") and request.path != "/api/registro":
        ms = (time.perf_counter() - g.t0) * 1000
        log.info("%s %s -> %s (%.0f ms) %s", request.method, request.path, resp.status_code, ms, g.detalle)
    return resp


@app.errorhandler(413)
def _grande(_):
    return error("La carga supera el límite de 25 MB. Sube menos archivos o archivos más pequeños.", "carga_grande", 413)


@app.errorhandler(404)
def _no_encontrado(_):
    if request.path.startswith("/api/"):
        return error("Ruta de API inexistente.", "no_encontrado", 404)
    return send_from_directory(WEB, "index.html"), 404


@app.errorhandler(500)
def _interno(_):
    return error("Error interno del servidor. Revisa el registro del backend.", "interno", 500)


def estado_inicial(*resultados):
    """«Requiere revisión» si cualquiera de los modelos aplicados tiene confianza baja."""
    minima = min(r["confianza"] for r in resultados if r)
    return "Requiere revisión" if minima < modelo.UMBRAL_CONFIANZA else "Clasificado"


def radicar(texto, asunto="", archivo="", origen="usuario", radicado=None):
    tipo, rama, tema = modelo.analizar(texto)
    return db.crear(texto, tipo, rama, tema, estado_inicial(tipo, rama, tema),
                    asunto=asunto, archivo=archivo, origen=origen, radicado=radicado)


# ───────────────────────── API ─────────────────────────
@app.get("/api/salud")
def salud():
    try:
        modelo.cargar_todos()
        ok, msg = True, "Modelos cargados."
    except modelo.ErrorModelo as e:
        ok, msg = False, str(e)
    g.detalle = f"modelo_ok={ok}"
    return jsonify({"ok": ok, "mensaje": msg, "modelos": modelo.info().get("modelos", {}), "entrenado": modelo.info().get("entrenado"),
                    "umbral_confianza": modelo.UMBRAL_CONFIANZA,
                    "formatos": sorted(SOPORTADOS) + [".doc (no soportado)"]}), (200 if ok else 503)


@app.get("/api/categorias")
def categorias():
    return jsonify({"categorias": [{"nombre": n, "descripcion": d, "plazo": db.PLAZOS[n][1]} for n, d in CATEGORIAS.items()],
                    "estados": db.ESTADOS, "integrantes": INTEGRANTES, "ramas": RAMAS, "temas": TEMAS, "min_caracteres": MIN_CHARS, "max_caracteres": MAX_CHARS,
                    "max_archivos": MAX_ARCHIVOS})


@app.post("/api/documentos")
def crear_documentos():
    """Radica uno o varios documentos: texto pegado (JSON) o archivos (multipart)."""
    asunto = ""
    entradas = []  # (nombre_mostrado, texto | None, ErrorArchivo | None)
    if request.is_json:
        cuerpo = request.get_json(silent=True) or {}
        asunto = str(cuerpo.get("asunto", "")).strip()[:120]
        texto = str(cuerpo.get("texto", "")).strip()
        if not texto:
            return error("El texto está vacío. Pega el contenido del documento o sube un archivo.", "texto_vacio", 400)
        if len(texto) < MIN_CHARS:
            return error(f"El texto es muy corto ({len(texto)} caracteres). Escribe al menos {MIN_CHARS}.", "texto_corto", 400)
        if len(texto) > MAX_CHARS:
            return error(f"El texto supera {MAX_CHARS} caracteres. Carga un fragmento más breve.", "texto_largo", 400)
        entradas.append(("texto pegado", texto, None))
    else:
        asunto = request.form.get("asunto", "").strip()[:120]
        archivos = [a for a in request.files.getlist("archivo") if a.filename]
        if not archivos:
            return error("No se recibió ningún archivo.", "sin_archivo", 400)
        if len(archivos) > MAX_ARCHIVOS:
            return error(f"Máximo {MAX_ARCHIVOS} archivos por envío.", "demasiados_archivos", 400)
        for a in archivos:
            try:
                entradas.append((a.filename, extraer_texto(a.filename, a.read()), None))
            except ErrorArchivo as e:
                entradas.append((a.filename, None, e))

    resultados, hubo_modelo_caido = [], False
    for nombre, texto, err in entradas:
        if err:
            resultados.append({"archivo": nombre, "ok": False, "error": str(err)})
            continue
        try:
            doc_id = radicar(texto, asunto=asunto, archivo="" if nombre == "texto pegado" else nombre)
        except modelo.ErrorModelo as e:
            hubo_modelo_caido = True
            resultados.append({"archivo": nombre, "ok": False, "error": str(e)})
            continue
        resultados.append({"archivo": nombre, "ok": True, "documento": db.obtener(doc_id)})

    ok = [r for r in resultados if r["ok"]]
    g.detalle = f"{len(ok)}/{len(resultados)} radicados " + "; ".join(
        f"#{r['documento']['id']}={r['documento']['categoria']}({r['documento']['confianza']:.0%})"
        f"/{r['documento']['rama']['categoria']}" + (f"/{r['documento']['tema']['categoria']}" if r['documento']['tema'] else "")
        for r in ok)
    if hubo_modelo_caido and not ok:
        return error(resultados[0]["error"], "modelo_no_disponible", 503)
    return jsonify({"resultados": resultados}), (200 if ok else 422)


@app.get("/api/documentos")
def listar_documentos():
    docs = db.listar(request.args.get("categoria"), request.args.get("estado"), request.args.get("q"),
                     request.args.get("rama"), request.args.get("tema"), request.args.get("revisor"))
    g.detalle = f"{len(docs)} documentos"
    return jsonify({"documentos": docs, "resumen": db.resumen()})


@app.get("/api/documentos/<int:doc_id>")
def obtener_documento(doc_id):
    d = db.obtener(doc_id)
    return jsonify(d) if d else error("El documento no existe.", "no_encontrado", 404)


@app.get("/api/documentos/<int:doc_id>/ficha.pdf")
def ficha_pdf(doc_id):
    d = db.obtener(doc_id)
    if not d:
        return error("El documento no existe.", "no_encontrado", 404)
    try:
        pdf = generar_pdf(d)
    except Exception as e:  # la ficha es opcional: un fallo no debe tumbar el servidor
        log.exception("Fallo al generar la ficha PDF")
        return error(f"No se pudo generar la ficha PDF: {e}", "ficha_fallida", 500)
    g.detalle = f"ficha #{doc_id} revisado_por={d['revisado_por']}"
    return pdf, 200, {"Content-Type": "application/pdf",
                      "Content-Disposition": f'attachment; filename="expediente_{doc_id}.pdf"'}


@app.put("/api/documentos/<int:doc_id>")
def actualizar_documento(doc_id):
    cuerpo = request.get_json(silent=True) or {}
    categoria, estado, nota = cuerpo.get("categoria"), cuerpo.get("estado"), cuerpo.get("nota")
    rama, tema = cuerpo.get("rama"), cuerpo.get("tema")
    revisores = cuerpo.get("revisado_por")
    if categoria is not None and categoria not in CATEGORIAS:
        return error("Categoría no válida.", "categoria_invalida", 400)
    if estado is not None and estado not in db.ESTADOS:
        return error("Estado no válido.", "estado_invalido", 400)
    if rama is not None and rama not in RAMAS:
        return error("Rama del derecho no válida.", "rama_invalida", 400)
    if tema is not None and tema not in TEMAS:
        return error("Asunto de tutela no válido.", "tema_invalido", 400)
    if revisores is not None:
        if not isinstance(revisores, list) or any(r not in INTEGRANTES for r in revisores):
            return error("Revisor no válido: elige integrantes de la lista del equipo.", "revisor_invalido", 400)
        revisores = list(dict.fromkeys(revisores))  # sin duplicados, conserva el orden
    cambia = any(v is not None for v in (categoria, estado, nota, rama, tema))
    if cambia and not revisores:
        return error("Indica quién revisó el documento (al menos una persona del equipo) para guardar los cambios.", "falta_revisor", 400)
    if nota is not None and len(str(nota)) > 1000:
        return error("La nota supera 1000 caracteres.", "nota_larga", 400)
    resultado = db.actualizar(doc_id, categoria, estado, None if nota is None else str(nota), rama, tema, revisores)
    if resultado is False:
        return error("El documento no existe.", "no_encontrado", 404)
    if resultado is not True:
        return error(resultado, "combinacion_invalida", 400)
    g.detalle = f"#{doc_id} categoria={categoria} rama={rama} tema={tema} estado={estado} revisado_por={revisores}"
    return jsonify(db.obtener(doc_id))


@app.get("/api/pruebas")
def pruebas():
    ruta = RAIZ / "evidencia" / "tabla_pruebas.json"
    if not ruta.exists():
        return jsonify({"disponible": False})
    return jsonify({"disponible": True, **json.loads(ruta.read_text(encoding="utf-8"))})


@app.get("/api/registro")
def registro():
    n = min(int(request.args.get("n", 40) or 40), 200)
    lineas = RUTA_LOG.read_text(encoding="utf-8").splitlines()[-n:] if RUTA_LOG.exists() else []
    return jsonify({"lineas": lineas})


# ───────────────────────── Páginas ─────────────────────────
PAGINAS = {"/": "index.html", "/bandeja": "bandeja.html", "/documento": "documento.html", "/guia": "guia.html"}
for _ruta, _archivo in PAGINAS.items():
    app.add_url_rule(_ruta, _archivo, (lambda a=_archivo: send_from_directory(WEB, a)))


@app.get("/<path:ruta>")
def estaticos(ruta):
    if ruta.startswith(("api/", ".")) or "/." in ruta:
        return _no_encontrado(None)
    return send_from_directory(WEB, ruta)


db.iniciar()
try:
    modelo.cargar_todos()
except modelo.ErrorModelo as e:
    log.info("INICIO sin modelo: %s", e)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("GESTOR_PUERTO", 5000)), debug=False)
