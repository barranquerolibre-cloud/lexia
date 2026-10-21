"""Pruebas de integración: levanta el backend REAL y lo llama por HTTP (no usa simulaciones).

Uso:  python pruebas/pruebas.py
Genera:
  evidencia/tabla_pruebas.md / .json   tabla caso | esperado | obtenido | estado | pendientes
  evidencia/registro_pruebas.log       registro del backend durante las pruebas
Usa una base de datos y un registro aparte para no mezclar con los datos del gestor.
"""
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVID = RAIZ / "evidencia"
EVID.mkdir(exist_ok=True)
PUERTO_OK, PUERTO_SIN_MODELO = 5055, 5056

# Textos NUEVOS: no están en datos/dataset.csv y usan un estilo distinto al de los ejemplos de entrenamiento.
T_TUTELA = ("Buenas tardes. Hace tres semanas me quitaron el servicio de diálisis en la clínica y desde entonces mi madre, "
            "que tiene setenta años, no ha podido recibir su tratamiento. La EPS dice que debo esperar una autorización "
            "que nunca llega. Pido al juez que ampare sus derechos fundamentales a la salud y a la vida y que ordene "
            "restablecer el servicio de inmediato.")
T_PETICION = ("Estimados señores de la Secretaría de Educación: les escribo para solicitar el certificado de estudios del "
              "año 2022 de mi hijo y que me indiquen en qué oficina puedo reclamarlo. En ejercicio del derecho de petición "
              "agradezco que la respuesta se envíe a mi correo electrónico.")
T_DEMANDA = ("Al Juzgado Civil Municipal: la parte demandante, mediante apoderado, formula demanda ejecutiva contra el "
             "demandado por la suma de dieciocho millones de pesos más intereses de mora, con base en la letra de cambio "
             "aceptada y vencida. Pretensiones: que se libre mandamiento de pago y se decrete el embargo de los bienes. "
             "Anexos: la letra de cambio y el poder.")
T_TRABAJO = ("Mi empleador terminó el contrato sin autorización del inspector de trabajo mientras yo estaba incapacitada. "
             "Pido por tutela que se proteja mi derecho al trabajo y que me reintegren al cargo que ocupaba.")
T_VITAL = ("Hace tres meses la administradora no consigna mi mesada de pensión y no tengo con qué comprar comida ni pagar los "
           "servicios. Solicito mediante tutela proteger mi mínimo vital y que se reanude el pago de inmediato.")
T_MERITO = ("Participé en el concurso de méritos de la alcaldía, quedé de primero en la lista de elegibles y todavía no me "
            "nombran en el cargo vacante. Acudo a la tutela para que se proteja mi acceso a cargos públicos por mérito.")
T_AMBIGUO = ("Llevo meses con un problema con la entidad y nadie me resuelve nada. Necesito que alguien revise mi caso "
             "porque esto me está afectando mucho y ya no sé a quién acudir.")


def pdf_con_texto(texto):
    import pymupdf
    doc = pymupdf.open()
    pagina = doc.new_page()
    pagina.insert_textbox(pymupdf.Rect(50, 50, 545, 780), texto, fontsize=11)
    return doc.tobytes()


def pdf_en_blanco():
    import pymupdf
    doc = pymupdf.open()
    doc.new_page()
    return doc.tobytes()


def docx_con_texto(texto):
    import docx
    d = docx.Document()
    d.add_paragraph(texto)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def multipart(campos, archivos):
    borde = "----lexia" + uuid.uuid4().hex
    cuerpo = b""
    for k, v in campos.items():
        cuerpo += f'--{borde}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for nombre, datos in archivos:
        cuerpo += (f'--{borde}\r\nContent-Disposition: form-data; name="archivo"; filename="{nombre}"\r\n'
                   "Content-Type: application/octet-stream\r\n\r\n").encode() + datos + b"\r\n"
    cuerpo += f"--{borde}--\r\n".encode()
    return cuerpo, f"multipart/form-data; boundary={borde}"


def llamar(puerto, metodo, ruta, json_cuerpo=None, archivos=None):
    url = f"http://127.0.0.1:{puerto}{ruta}"
    if archivos is not None:
        datos, tipo = multipart({"asunto": "prueba"}, archivos)
    elif json_cuerpo is not None:
        datos, tipo = json.dumps(json_cuerpo).encode(), "application/json"
    else:
        datos, tipo = None, None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"Content-Type": tipo} if tipo else {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def levantar(puerto, extra_env):
    env = {**os.environ, "GESTOR_PUERTO": str(puerto), "PYTHONIOENCODING": "utf-8", **extra_env}
    p = subprocess.Popen([sys.executable, str(RAIZ / "backend" / "app.py")], env=env, cwd=RAIZ / "backend",
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{puerto}/api/categorias", timeout=1)
            return p
        except Exception:
            time.sleep(0.5)
    p.kill()
    raise SystemExit(f"El backend no arrancó en el puerto {puerto}")


def main():
    for f in ("gestor_pruebas.db", "registro_pruebas.log"):
        (EVID / f).unlink(missing_ok=True)
    env_ok = {"GESTOR_DB": str(EVID / "gestor_pruebas.db"), "GESTOR_LOG": str(EVID / "registro_pruebas.log")}
    env_caido = {"GESTOR_DB": str(EVID / "gestor_pruebas_sin_modelo.db"), "GESTOR_LOG": str(EVID / "registro_pruebas.log"),
                 "GESTOR_MODELOS_DIR": str(EVID / "sin_modelos")}
    (EVID / "gestor_pruebas_sin_modelo.db").unlink(missing_ok=True)
    servidores = [levantar(PUERTO_OK, env_ok), levantar(PUERTO_SIN_MODELO, env_caido)]
    filas = []

    def caso(nombre, esperado, f):
        try:
            obtenido, ok, pendiente = f()
        except Exception as e:  # una excepción en la prueba es un fallo del caso, no del script
            obtenido, ok, pendiente = f"Excepción: {e}", False, "Revisar la prueba"
        filas.append({"id": len(filas) + 1, "caso": nombre, "esperado": esperado, "obtenido": obtenido,
                      "estado": "PASA" if ok else "FALLA", "pendiente": pendiente})
        print(f"{filas[-1]['id']:>2}. {'PASA ' if ok else 'FALLA'} {nombre} -> {obtenido}")

    def clasifica(texto, esperada, archivos=None, tema=None, rama=None):
        def f():
            s, d = (llamar(PUERTO_OK, "POST", "/api/documentos", archivos=archivos) if archivos
                    else llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": texto}))
            r = d["resultados"][0]
            if not r["ok"]:
                return f"HTTP {s}: {r['error']}", False, "Revisar extracción"
            doc = r["documento"]
            t = (doc["tema"] or {}).get("categoria")
            obtenido = (f"HTTP {s}: {doc['categoria']} ({doc['confianza']:.0%}) · rama {doc['rama']['categoria']} "
                        f"({doc['rama']['confianza']:.0%}) · asunto {t or '—'} · estado «{doc['estado']}»")
            ok = doc["categoria"] == esperada and t == tema and (rama is None or doc["rama"]["categoria"] == rama)
            return obtenido, ok, "" if ok else "Modelo se equivocó: revisar datos"
        return f

    try:
        def salud():
            s, d = llamar(PUERTO_OK, "GET", "/api/salud")
            return f"HTTP {s}: modelo_ok={d['ok']}, modelos={list(d['modelos'])}", s == 200 and d["ok"] and len(d["modelos"]) == 3, ""
        caso("Salud del backend", "HTTP 200 y los 3 modelos cargados", salud)
        caso("Tutela nueva sobre trabajo", "Tutela · asunto Derecho al trabajo", clasifica(T_TRABAJO, "Tutela", tema="Derecho al trabajo"))
        caso("Tutela nueva sobre mínimo vital", "Tutela · asunto Mínimo vital", clasifica(T_VITAL, "Tutela", tema="Mínimo vital"))
        caso("Tutela nueva sobre meritocracia", "Tutela · asunto Meritocracia", clasifica(T_MERITO, "Tutela", tema="Meritocracia"))
        caso("Derecho de petición nuevo", "Derecho de petición · sin asunto de tutela", clasifica(T_PETICION, "Derecho de petición"))
        caso("Demanda nueva (ejecutiva)", "Demanda · rama Derecho civil · sin asunto", clasifica(T_DEMANDA, "Demanda", rama="Derecho civil"))

        def tutela_fuera_de_lab2():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_TUTELA})
            doc = d["resultados"][0]["documento"]
            t = doc["tema"]
            return (f"HTTP {s}: {doc['categoria']}, asunto forzado a «{t['categoria'] if t else '—'}» ({t['confianza'] if t else 0:.0%}), "
                    f"estado «{doc['estado']}»", s == 200 and doc["categoria"] == "Tutela" and t is not None,
                    "Limitación: el Lab 2 no tiene la categoría «Salud»; una persona debe revisar el asunto")
        caso("Tutela de salud (fuera de las 3 categorías del Lab 2)", "Se clasifica como Tutela y se deja el asunto a revisión humana", tutela_fuera_de_lab2)

        def ambiguo():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_AMBIGUO})
            doc = d["resultados"][0]["documento"]
            regla = (doc["confianza"] < 0.55) == (doc["estado"] == "Requiere revisión")
            return (f"HTTP {s}: {doc['categoria']} ({doc['confianza']:.0%}), estado «{doc['estado']}»", s == 200 and regla,
                    "Un humano debe revisar este caso (texto ambiguo a propósito)")
        caso("Texto ambiguo", "HTTP 200; si la confianza < 55 % queda «Requiere revisión»", ambiguo)

        def vacio():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": "   "})
            return f"HTTP {s}: {d.get('error')}", s == 400 and d.get("codigo") == "texto_vacio", ""
        caso("Texto vacío", "HTTP 400 y mensaje que pide contenido", vacio)

        def corto():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": "Hola, necesito ayuda"})
            return f"HTTP {s}: {d.get('error')}", s == 400 and d.get("codigo") == "texto_corto", ""
        caso("Texto demasiado corto", "HTTP 400 (mínimo 40 caracteres)", corto)

        caso("Archivo PDF con texto", "Tutela · asunto Derecho al trabajo", clasifica(None, "Tutela", [("tutela_trabajo.pdf", pdf_con_texto(T_TRABAJO))], tema="Derecho al trabajo"))
        caso("Archivo Word (.docx)", "Derecho de petición",
             clasifica(None, "Derecho de petición", [("peticion_certificado.docx", docx_con_texto(T_PETICION))]))
        caso("Archivo de texto (.txt)", "Demanda", clasifica(None, "Demanda", [("demanda_ejecutiva.txt", T_DEMANDA.encode())]))

        def rechazo(nombre, datos, fragmento):
            def f():
                s, d = llamar(PUERTO_OK, "POST", "/api/documentos", archivos=[(nombre, datos)])
                msg = d["resultados"][0]["error"] if "resultados" in d else d.get("error", "")
                return f"HTTP {s}: {msg}", s == 422 and fragmento in msg, ""
            return f
        caso("Word antiguo (.doc)", "HTTP 422 y pide convertir a .docx", rechazo("viejo.doc", b"x" * 80, ".docx"))
        caso("PDF escaneado sin texto", "HTTP 422 y explica que no hay texto/OCR", rechazo("escaneo.pdf", pdf_en_blanco(), "OCR"))
        caso("Formato no soportado (.exe)", "HTTP 422 y lista de formatos", rechazo("virus.exe", b"MZ" * 40, "no soportado"))

        def lote():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos",
                          archivos=[("a.txt", T_TUTELA.encode()), ("malo.doc", b"x" * 50), ("b.txt", T_PETICION.encode())])
            oks = [r["ok"] for r in d["resultados"]]
            return f"HTTP {s}: resultados por archivo = {oks}", s == 200 and oks == [True, False, True], ""
        caso("Lote de 3 archivos con uno inválido", "Procesa los válidos y reporta el inválido", lote)

        def corregir():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_AMBIGUO})
            orig = d["resultados"][0]["documento"]
            nueva = "Demanda" if orig["categoria"] != "Demanda" else "Tutela"  # siempre distinta a la del modelo
            rama_nueva = "Derecho civil" if orig["rama"]["categoria"] != "Derecho civil" else "Derecho laboral"
            s2, d2 = llamar(PUERTO_OK, "PUT", f"/api/documentos/{orig['id']}", json_cuerpo={"categoria": nueva, "rama": rama_nueva, "estado": "En revisión", "nota": "Corregido en prueba", "revisado_por": ["Willigton Herrera", "Leidy Laura Blandon"]})
            hist = " | ".join(e["evento"] for e in d2.get("eventos", []))
            ok = s2 == 200 and d2["categoria"] == nueva and d2["corregido"] and d2["estado"] == "En revisión" and "corregid" in hist and d2["rama"]["categoria"] == rama_nueva and d2["revisado_por"] == ["Willigton Herrera", "Leidy Laura Blandon"]
            return f"HTTP {s2}: categoría={d2.get('categoria')}, estado={d2.get('estado')}, corregido={d2.get('corregido')}", ok, ""
        caso("Corrección humana de categoría y estado", "Se guarda y queda en el historial", corregir)

        def corregir_asunto():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_TRABAJO})
            orig = d["resultados"][0]["documento"]
            nuevo = "Mínimo vital" if orig["tema"]["categoria"] != "Mínimo vital" else "Meritocracia"
            s2, d2 = llamar(PUERTO_OK, "PUT", f"/api/documentos/{orig['id']}", json_cuerpo={"tema": nuevo, "revisado_por": ["Alejadro Escobar"]})
            hist = " | ".join(e["evento"] for e in d2.get("eventos", []))
            ok = s2 == 200 and d2["tema"]["categoria"] == nuevo and d2["tema"]["modelo"] == orig["tema"]["categoria"] and "Asunto corregido" in hist
            return f"HTTP {s2}: asunto {orig['tema']['categoria']} → {d2['tema']['categoria']}; el modelo propuso {d2['tema']['modelo']}", ok, ""
        caso("Corrección humana del asunto de la tutela", "Se guarda, conserva lo que propuso el modelo y queda en el historial", corregir_asunto)

        def asunto_en_peticion():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_PETICION})
            did = d["resultados"][0]["documento"]["id"]
            s2, d2 = llamar(PUERTO_OK, "PUT", f"/api/documentos/{did}", json_cuerpo={"tema": "Mínimo vital", "revisado_por": ["Alejadro Escobar"]})
            return f"HTTP {s2}: {d2.get('error')}", s2 == 400 and d2.get("codigo") == "combinacion_invalida", ""
        caso("Asunto de tutela en un documento que no es tutela", "HTTP 400 con mensaje claro", asunto_en_peticion)

        def sin_revisor():
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_VITAL})
            did = d["resultados"][0]["documento"]["id"]
            s2, d2 = llamar(PUERTO_OK, "PUT", f"/api/documentos/{did}", json_cuerpo={"estado": "En revisión"})
            return f"HTTP {s2}: {d2.get('error')}", s2 == 400 and d2.get("codigo") == "falta_revisor", ""
        caso("Guardar una revisión sin indicar quién revisó", "HTTP 400 que pide al menos un revisor del equipo", sin_revisor)

        def revisor_falso():
            s2, d2 = llamar(PUERTO_OK, "PUT", "/api/documentos/1", json_cuerpo={"estado": "Atendido", "revisado_por": ["Persona Inventada"]})
            return f"HTTP {s2}: {d2.get('error')}", s2 == 400 and d2.get("codigo") == "revisor_invalido", ""
        caso("Revisor que no pertenece al equipo", "HTTP 400 (solo se aceptan los integrantes de la lista)", revisor_falso)

        def ficha():
            import pypdf
            s, d = llamar(PUERTO_OK, "POST", "/api/documentos", json_cuerpo={"texto": T_MERITO})
            did = d["resultados"][0]["documento"]["id"]
            llamar(PUERTO_OK, "PUT", f"/api/documentos/{did}", json_cuerpo={"estado": "Atendido", "revisado_por": ["Cenith del Carmen Castro", "David Alfoso Londoño"]})
            with urllib.request.urlopen(f"http://127.0.0.1:{PUERTO_OK}/api/documentos/{did}/ficha.pdf", timeout=30) as r:
                datos, tipo = r.read(), r.headers["Content-Type"]
            texto = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(datos)).pages)
            ok = datos[:4] == b"%PDF" and tipo == "application/pdf" and "Cenith del Carmen Castro" in texto and "David Alfoso Londoño" in texto
            return f"PDF de {len(datos) // 1024} KB; incluye los nombres de los revisores: {ok}", ok, ""
        caso("Ficha PDF del expediente con los revisores", "PDF válido que contiene el nombre de cada persona que revisó", ficha)

        def por_revisor():
            s, d = llamar(PUERTO_OK, "GET", "/api/documentos?revisor=" + urllib.parse.quote("Willigton Herrera"))
            ok = s == 200 and d["documentos"] and all("Willigton Herrera" in x["revisado_por"] for x in d["documentos"])
            return f"HTTP {s}: {len(d['documentos'])} expedientes revisados por Willigton Herrera", bool(ok), ""
        caso("Bandeja filtrada por revisor", "Solo expedientes revisados por esa persona", por_revisor)

        def estado_malo():
            s, d = llamar(PUERTO_OK, "PUT", "/api/documentos/1", json_cuerpo={"estado": "Inventado"})
            return f"HTTP {s}: {d.get('error')}", s == 400, ""
        caso("Estado inválido", "HTTP 400", estado_malo)

        def inexistente():
            s, d = llamar(PUERTO_OK, "GET", "/api/documentos/99999")
            return f"HTTP {s}: {d.get('error')}", s == 404, ""
        caso("Expediente inexistente", "HTTP 404 con mensaje", inexistente)

        def sin_modelo():
            s, d = llamar(PUERTO_SIN_MODELO, "POST", "/api/documentos", json_cuerpo={"texto": T_TUTELA})
            return f"HTTP {s}: {d.get('error')}", s == 503 and d.get("codigo") == "modelo_no_disponible", ""
        caso("Fallo de carga del modelo", "HTTP 503 con mensaje claro", sin_modelo)

        def listar():
            s, d = llamar(PUERTO_OK, "GET", "/api/documentos?categoria=Tutela")
            ok = s == 200 and d["documentos"] and all(x["categoria"] == "Tutela" for x in d["documentos"])
            return f"HTTP {s}: {len(d['documentos'])} expedientes de Tutela en la bandeja", bool(ok), ""
        caso("Bandeja filtrada por categoría", "Solo expedientes de la categoría pedida", listar)
    finally:
        for p in servidores:
            p.terminate()

    pasan = sum(f["estado"] == "PASA" for f in filas)
    manuales = [
        {"caso": "Interfaz con el backend apagado", "esperado": "La página muestra «Backend sin conexión» y un mensaje claro",
         "obtenido": "Verificado en navegador (ver evidencia/capturas)", "pendiente": "Repetir antes de entregar"},
    ]
    resumen = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "total": len(filas), "pasan": pasan, "filas": filas, "manuales": manuales}
    (EVID / "tabla_pruebas.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# Tabla de pruebas de integración\n\nEjecutada: {resumen['fecha']} · {pasan}/{len(filas)} casos pasan\n",
          "| # | Caso | Resultado esperado | Resultado obtenido | Estado | Errores / pendientes |", "|---|---|---|---|---|---|"]
    for f in filas:
        md.append(f"| {f['id']} | {f['caso']} | {f['esperado']} | {f['obtenido'].replace('|', '/')} | {f['estado']} | {f['pendiente']} |")
    (EVID / "tabla_pruebas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n{pasan}/{len(filas)} casos pasan -> evidencia/tabla_pruebas.md")
    return 0 if pasan == len(filas) else 1


if __name__ == "__main__":
    sys.exit(main())
