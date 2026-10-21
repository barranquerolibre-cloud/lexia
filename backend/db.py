"""Persistencia SQLite del gestor: expedientes, estados e historial."""
import json
import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

RUTA_DB = Path(os.environ.get("GESTOR_DB") or Path(__file__).resolve().parent / "gestor.db")

ESTADOS = ["Clasificado", "Requiere revisión", "En revisión", "Atendido"]
# Días hábiles de referencia (sin festivos). Tutela: Decreto 2591/1991 art. 29; petición: Ley 1755/2015
# (15 días hábiles). El plazo de demanda es una referencia INTERNA de revisión, no un término legal.
PLAZOS = {"Tutela": (10, "10 días hábiles para el fallo"),
          "Derecho de petición": (15, "15 días hábiles para responder"),
          "Demanda": (30, "30 días hábiles (referencia interna de revisión)")}


def conexion():
    c = sqlite3.connect(RUTA_DB)
    c.row_factory = sqlite3.Row
    return c


def iniciar():
    with conexion() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS documentos(
            id INTEGER PRIMARY KEY AUTOINCREMENT, asunto TEXT, archivo TEXT, texto TEXT NOT NULL,
            categoria_modelo TEXT NOT NULL, categoria TEXT NOT NULL, confianza REAL NOT NULL,
            probabilidades TEXT NOT NULL, estado TEXT NOT NULL, fecha_radicacion TEXT NOT NULL,
            fecha_limite TEXT NOT NULL, origen TEXT NOT NULL DEFAULT 'usuario', nota TEXT DEFAULT '',
            analisis TEXT NOT NULL DEFAULT '{}', revisado_por TEXT NOT NULL DEFAULT '[]');
        CREATE TABLE IF NOT EXISTS eventos(
            id INTEGER PRIMARY KEY AUTOINCREMENT, documento_id INTEGER NOT NULL,
            fecha TEXT NOT NULL, evento TEXT NOT NULL);
        """)
        columnas = {r["name"] for r in c.execute("PRAGMA table_info(documentos)")}
        for nombre, definicion in (("analisis", "TEXT NOT NULL DEFAULT '{}'"), ("revisado_por", "TEXT NOT NULL DEFAULT '[]'")):
            if nombre not in columnas:  # bases creadas por versiones anteriores
                c.execute(f"ALTER TABLE documentos ADD COLUMN {nombre} {definicion}")


def vacia():
    with conexion() as c:
        return c.execute("SELECT COUNT(*) FROM documentos").fetchone()[0] == 0


def sumar_habiles(desde, n):
    d = desde
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def _evento(c, doc_id, texto, cuando=None):
    c.execute("INSERT INTO eventos(documento_id,fecha,evento) VALUES(?,?,?)",
              (doc_id, (cuando or datetime.now()).isoformat(timespec="seconds"), texto))


def _guardable(r):
    """Resultado del modelo -> estructura que se guarda (categoría del modelo y categoría vigente)."""
    if r is None:
        return None
    return {"modelo": r["categoria"], "categoria": r["categoria"], "confianza": r["confianza"],
            "probabilidades": r["probabilidades"]}


def crear(texto, tipo, rama, tema, estado, asunto="", archivo="", origen="usuario", radicado=None):
    """tipo, rama y tema son los dicts que devuelve modelo.clasificar (tema puede ser None)."""
    radicado = radicado or date.today()
    categoria = tipo["categoria"]
    limite = sumar_habiles(radicado, PLAZOS[categoria][0])
    analisis = {"rama": _guardable(rama), "tema": _guardable(tema)}
    with conexion() as c:
        cur = c.execute(
            "INSERT INTO documentos(asunto,archivo,texto,categoria_modelo,categoria,confianza,probabilidades,"
            "estado,fecha_radicacion,fecha_limite,origen,analisis) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (asunto, archivo, texto, categoria, categoria, tipo["confianza"], json.dumps(tipo["probabilidades"]), estado,
             radicado.isoformat(), limite.isoformat(), origen, json.dumps(analisis)))
        doc_id = cur.lastrowid
        cuando = datetime.combine(radicado, datetime.min.time().replace(hour=9))
        _evento(c, doc_id, "Radicado", cuando)
        _evento(c, doc_id, f"Tipo de documento: «{categoria}» ({tipo['confianza']:.0%})", cuando)
        _evento(c, doc_id, f"Rama del derecho (Lab 1): «{rama['categoria']}» ({rama['confianza']:.0%})", cuando)
        if tema:
            _evento(c, doc_id, f"Asunto de la tutela (Lab 2): «{tema['categoria']}» ({tema['confianza']:.0%})", cuando)
        if estado == "Requiere revisión":
            _evento(c, doc_id, "Confianza baja en al menos un modelo: requiere revisión humana", cuando)
    return doc_id


def _fila(r, con_texto):
    d = dict(r)
    d["probabilidades"] = json.loads(d["probabilidades"])
    analisis = json.loads(d.pop("analisis") or "{}")
    d["rama"], d["tema"] = analisis.get("rama"), analisis.get("tema")
    d["revisado_por"] = json.loads(d["revisado_por"] or "[]")
    limite = date.fromisoformat(d["fecha_limite"])
    d["dias_restantes"] = (limite - date.today()).days
    d["vencido"] = d["estado"] != "Atendido" and d["dias_restantes"] < 0
    d["corregido"] = d["categoria"] != d["categoria_modelo"]
    d["plazo"] = PLAZOS[d["categoria"]][1]
    if not con_texto:
        d["extracto"] = (d["texto"][:180] + "…") if len(d["texto"]) > 180 else d["texto"]
        del d["texto"]
    return d


def listar(categoria=None, estado=None, q=None, rama=None, tema=None, revisor=None):
    sql, args = "SELECT * FROM documentos WHERE 1=1", []
    if categoria:
        sql += " AND categoria=?"
        args.append(categoria)
    if estado:
        sql += " AND estado=?"
        args.append(estado)
    if q:
        sql += " AND (texto LIKE ? OR asunto LIKE ? OR archivo LIKE ?)"
        args += [f"%{q}%"] * 3
    sql += " ORDER BY id DESC"
    with conexion() as c:
        docs = [_fila(r, False) for r in c.execute(sql, args)]
    if rama:
        docs = [d for d in docs if d["rama"] and d["rama"]["categoria"] == rama]
    if tema:
        docs = [d for d in docs if d["tema"] and d["tema"]["categoria"] == tema]
    if revisor:
        docs = [d for d in docs if revisor in d["revisado_por"]]
    return docs


def obtener(doc_id):
    with conexion() as c:
        r = c.execute("SELECT * FROM documentos WHERE id=?", (doc_id,)).fetchone()
        if not r:
            return None
        d = _fila(r, True)
        d["eventos"] = [dict(e) for e in c.execute(
            "SELECT fecha, evento FROM eventos WHERE documento_id=? ORDER BY id", (doc_id,))]
        return d


def actualizar(doc_id, categoria=None, estado=None, nota=None, rama=None, tema=None, revisores=None):
    """Revisión humana. Devuelve False si no existe, o un texto de error si la combinación no es válida."""
    with conexion() as c:
        r = c.execute("SELECT * FROM documentos WHERE id=?", (doc_id,)).fetchone()
        if not r:
            return False
        analisis = json.loads(r["analisis"] or "{}")
        tipo_final = categoria or r["categoria"]
        if tema and tipo_final != "Tutela":
            return "El asunto de la tutela solo aplica a documentos de tipo Tutela."
        if categoria and categoria != r["categoria"]:
            limite = sumar_habiles(date.fromisoformat(r["fecha_radicacion"]), PLAZOS[categoria][0])
            c.execute("UPDATE documentos SET categoria=?, fecha_limite=? WHERE id=?",
                      (categoria, limite.isoformat(), doc_id))
            _evento(c, doc_id, f"Tipo corregido por una persona: «{r['categoria']}» → «{categoria}»")
            if categoria != "Tutela" and analisis.get("tema"):
                analisis["tema"] = None
                _evento(c, doc_id, "Se retiró el asunto de la tutela (el documento ya no es una tutela)")
        if rama and analisis.get("rama") and rama != analisis["rama"]["categoria"]:
            _evento(c, doc_id, f"Rama corregida por una persona: «{analisis['rama']['categoria']}» → «{rama}»")
            analisis["rama"]["categoria"] = rama
        if tema:
            actual = analisis.get("tema")
            if not actual:
                analisis["tema"] = {"modelo": None, "categoria": tema, "confianza": 0.0, "probabilidades": {}}
                _evento(c, doc_id, f"Asunto de la tutela asignado por una persona: «{tema}»")
            elif tema != actual["categoria"]:
                _evento(c, doc_id, f"Asunto corregido por una persona: «{actual['categoria']}» → «{tema}»")
                actual["categoria"] = tema
        c.execute("UPDATE documentos SET analisis=? WHERE id=?", (json.dumps(analisis), doc_id))
        if estado and estado != r["estado"]:
            c.execute("UPDATE documentos SET estado=? WHERE id=?", (estado, doc_id))
            _evento(c, doc_id, f"Estado: {r['estado']} → {estado}")
        if nota is not None and nota != r["nota"]:
            c.execute("UPDATE documentos SET nota=? WHERE id=?", (nota, doc_id))
            _evento(c, doc_id, "Nota de revisión actualizada")
        if revisores:
            c.execute("UPDATE documentos SET revisado_por=? WHERE id=?", (json.dumps(revisores, ensure_ascii=False), doc_id))
            _evento(c, doc_id, "Revisión humana registrada por: " + ", ".join(revisores))
    return True


def resumen():
    docs = listar()
    por_cat, por_est, por_tema = {}, {}, {}
    for d in docs:
        por_cat[d["categoria"]] = por_cat.get(d["categoria"], 0) + 1
        por_est[d["estado"]] = por_est.get(d["estado"], 0) + 1
        if d["tema"]:
            por_tema[d["tema"]["categoria"]] = por_tema.get(d["tema"]["categoria"], 0) + 1
    return {"total": len(docs), "por_categoria": por_cat, "por_estado": por_est, "por_tema": por_tema,
            "vencidos": sum(d["vencido"] for d in docs),
            "requieren_revision": por_est.get("Requiere revisión", 0)}
