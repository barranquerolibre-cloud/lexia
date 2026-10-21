"""Ficha PDF de un expediente: resultado de la clasificación y persona(s) que lo revisaron."""
import io
from datetime import date, datetime
from html import escape

import pymupdf

CSS = """
body{font-family:sans-serif;font-size:10pt;color:#2b2540}
h1{font-size:19pt;color:#3a2d63;margin-bottom:2px}
h2{font-size:12pt;color:#4938b6;margin-top:16px;margin-bottom:4px}
p{margin:3px 0;line-height:1.35}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid #cfc6e3;padding:5px;text-align:left;vertical-align:top}
th{background:#f1ecfa}
.aviso{background:#fff3d9;padding:6px}
.ok{background:#e4f6ec;padding:6px}
.pie{font-size:8pt;color:#6b6780;margin-top:14px}
.texto{background:#f8f6fc;padding:7px;font-size:9.5pt}
"""


def _pct(x):
    return f"{x:.0%}"


def _fila_modelo(nombre, lab, r, manual_ok=True):
    if r is None:
        return f"<tr><td>{escape(nombre)}</td><td>{escape(lab)}</td><td colspan='3'>No aplica (solo se calcula en tutelas)</td></tr>"
    modelo = r.get("modelo")
    propuesta = escape(modelo) if modelo else "— (asignado por una persona)"
    conf = _pct(r["confianza"]) if modelo else "—"
    final = escape(r["categoria"])
    return (f"<tr><td>{escape(nombre)}</td><td>{escape(lab)}</td><td>{propuesta}</td><td>{conf}</td>"
            f"<td><b>{final}</b></td></tr>")


def generar_pdf(d):
    """d es el dict que devuelve db.obtener(). Devuelve los bytes del PDF."""
    revisores = d["revisado_por"]
    if revisores:
        bloque_rev = f"<p class='ok'><b>Revisado por:</b> {escape(', '.join(revisores))}</p>"
    else:
        bloque_rev = "<p class='aviso'><b>Revisión humana pendiente:</b> ninguna persona ha confirmado todavía esta clasificación.</p>"
    nota = f"<p><b>Nota de revisión:</b> {escape(d['nota'])}</p>" if d.get("nota") else ""
    eventos = "".join(
        f"<tr><td>{escape(datetime.fromisoformat(e['fecha']).strftime('%Y-%m-%d %H:%M'))}</td><td>{escape(e['evento'])}</td></tr>"
        for e in d["eventos"])
    texto = escape(d["texto"]).replace("\n", "<br>")
    titulo = escape(d["asunto"] or d["archivo"] or f"Expediente #{d['id']}")
    venc = "Atendido" if d["estado"] == "Atendido" else escape(d["fecha_limite"])
    html = f"""
    <h1>Ficha de clasificación · Expediente #{d['id']}</h1>
    <p><b>{titulo}</b>{' · archivo: ' + escape(d['archivo']) if d['archivo'] and d['asunto'] else ''}</p>
    <p>Radicado: {escape(d['fecha_radicacion'])} · Estado: <b>{escape(d['estado'])}</b> · Plazo de referencia: {escape(d['plazo'])} (vence: {venc})</p>
    {bloque_rev}
    {nota}
    <h2>Clasificación</h2>
    <table><tr><th>Modelo</th><th>Origen</th><th>Propuesta del modelo</th><th>Confianza</th><th>Categoría vigente</th></tr>
    {_fila_modelo('Tipo de documento', 'Gestor', {'modelo': d['categoria_modelo'], 'categoria': d['categoria'], 'confianza': d['confianza']})}
    {_fila_modelo('Rama del derecho', 'Laboratorio 1', d['rama'])}
    {_fila_modelo('Asunto de la tutela', 'Laboratorio 2', d['tema'])}
    </table>
    <h2>Texto del documento</h2>
    <p class='texto'>{texto}</p>
    <h2>Historial</h2>
    <table><tr><th>Fecha</th><th>Evento</th></tr>{eventos}</table>
    <p class='pie'>Generado el {date.today().isoformat()} por Lexia. La clasificación automática orienta; no sustituye el criterio jurídico de la persona que revisa.</p>
    """
    buf = io.BytesIO()
    escritor = pymupdf.DocumentWriter(buf)
    pagina = pymupdf.paper_rect("a4")
    area = pagina + (46, 46, -46, -46)
    historia = pymupdf.Story(html=html, user_css=CSS)
    mas = 1
    while mas:
        dispositivo = escritor.begin_page(pagina)
        mas, _ = historia.place(area)
        historia.draw(dispositivo)
        escritor.end_page()
    escritor.close()
    return buf.getvalue()
