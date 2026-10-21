from pathlib import Path
import pymupdf

BASE = Path(__file__).parent
CSS = """body {font-family: sans-serif; font-size:11pt; color:#25364a;}
h1 {font-size:23pt; color:#163d59; margin-bottom:12px;}
h2 {font-size:13pt; color:#176b78; margin-top:18px; margin-bottom:7px;}
p {line-height:1.45; margin:7px 0;}
table {border-collapse:collapse; width:100%; font-size:10.5pt;}
td,th {border:1px solid #c9d6df; padding:9px; text-align:left;}
th {background:#eaf1f5;}
.nota {background:#edf4f7; padding:11px; font-size:10pt;}
"""

PAGES = [
('Laboratorio 1', 'Clasificar documentos jurídicos', '''
<h2>Solución propuesta</h2>
<p>Usar <b>Laboratorio1_Clasificacion_Juridica.ipynb</b> en Google Colab para clasificar textos en <b>derecho laboral, civil o administrativo</b>.</p>
<p><b>Funcionamiento:</b> texto → limpieza → representación numérica (TF-IDF) → modelo → categoría predicha.</p>
<h2>Qué hacer puntualmente</h2>
<table><tr><th>Paso</th><th>Acción</th></tr>
<tr><td>1. Preparar</td><td>Completar los integrantes (máximo 4). Revisar los 120 ejemplos del cuaderno: 40 por categoría.</td></tr>
<tr><td>2. Ejecutar</td><td>Abrir en Colab y ejecutar todas las celdas. Revisar la limpieza, la conversión del texto a números y el entrenamiento.</td></tr>
<tr><td>3. Evaluar</td><td>Leer el porcentaje de aciertos y la matriz de confusión. Identificar qué categorías confunde y mostrar errores concretos.</td></tr>
<tr><td>4. Probar</td><td>Usar mínimo 3 textos nuevos, distintos de los de entrenamiento. Registrar categoría esperada y predicha. Conviene uno por categoría.</td></tr>
<tr><td>5. Interpretar</td><td>Explicar por qué falla y en qué casos necesitaría revisión humana.</td></tr></table>
<h2>Ejemplos de los asuntos</h2>
<p><b>Laboral:</b> salarios o prestaciones no pagadas.<br><b>Civil:</b> incumplimiento de compraventa entre particulares.<br><b>Administrativo:</b> impugnación de una sanción de una autoridad pública.</p>
<h2>Qué entregar</h2>
<p>Prototipo funcional y presentación que responda: <b>qué problema resolvieron, cómo lo resolvieron, qué resultados obtuvieron, en qué se equivocó y si podría utilizarse realmente en Derecho</b>.</p>
<p class="nota"><b>Ya existe:</b> el cuaderno tiene desarrollo y resultados guardados. Completar nombres y volver a ejecutarlo para confirmar las cifras antes de presentarlas.</p>
'''),
('Laboratorio 2', 'Diseñar un clasificador propio', '''
<h2>Solución propuesta</h2>
<p>Organizar tutelas por su <b>asunto principal</b>. Usuario propuesto: una persona que recibe tutelas y las distribuye para revisión jurídica.</p>
<table><tr><th>Categoría</th><th>Criterio propuesto</th></tr>
<tr><td>Derecho al trabajo</td><td>La pretensión principal busca proteger el vínculo laboral o conseguir un reintegro.</td></tr>
<tr><td>Mínimo vital</td><td>Busca recursos indispensables para subsistir, como salarios o mesadas.</td></tr>
<tr><td>Meritocracia</td><td>Trata de concursos, listas de elegibles o acceso por mérito a cargos públicos.</td></tr></table>
<p>Si se mezclan asuntos, decidir por la pretensión principal. Documentar casos ambiguos y ejemplos de lo que no pertenece a cada categoría.</p>
<h2>Qué hacer puntualmente</h2>
<p><b>1. Diseño:</b> describir el problema (3 a 5 líneas), usuario, categorías, criterios, fuentes, cantidades y limpieza. Justificar representatividad en 5 a 8 líneas: variedad, sesgos y casos faltantes.</p>
<p><b>2. Datos:</b> reunir mínimo <b>15 ejemplos por categoría: 45 en total</b>. Se permiten fragmentos de 1 o 2 párrafos. Anonimizar textos reales y revisar los generados con IA.</p>
<p><b>3. Revisión cruzada:</b> cada integrante clasifica 5 ejemplos que no escribió. Comparar, corregir desacuerdos y registrar lo aprendido.</p>
<p><b>4. Entrenamiento:</b> usar <b>Laboratorio1_clasificador_tutelas.ipynb</b>. Revisar etiquetas sugeridas y completar quién las aprobó.</p>
<p><b>5. Análisis:</b> en máximo 10 líneas, explicar dónde falla más, si falló el modelo o el criterio/etiqueta y qué revisión humana necesita.</p>
<h2>Qué entregar</h2>
<p><b>Documento de diseño + dataset + notebook entrenado.</b><br>Columnas del dataset: <b>id, texto, categoria, origen, revisado_por</b>.</p>
<p class="nota"><b>Ya existe:</b> cuaderno de apoyo. No se encontraron el diseño ni el dataset independiente. Verificar 15 ejemplos revisados por categoría. La guía permite entre 3 y 5 categorías; esta propuesta usa 3.</p>
'''),
('Laboratorio 3', 'Conectar la pantalla con el modelo', '''
<h2>Solución propuesta</h2>
<p>Crear <b>Clasificador de Tutelas</b> con Streamlit (pantalla en Python) y el modelo del laboratorio 2. El usuario pega un texto, pulsa <b>Clasificar</b> y recibe una categoría real.</p>
<h2>Qué construir puntualmente</h2>
<table><tr><th>Parte</th><th>Implementación propuesta</th></tr>
<tr><td>Modelo</td><td>Guardar y cargar el procesamiento TF-IDF y el clasificador entrenado, juntos.</td></tr>
<tr><td>Pantalla</td><td>Nombre de la aplicación, cuadro para pegar texto, botón para procesar y espacio para resultados.</td></tr>
<tr><td>Conexión</td><td>El botón envía el texto a una función de backend que aplica la preparación y ejecuta el modelo.</td></tr>
<tr><td>Respuesta</td><td>Mostrar la categoría devuelta por el modelo. Añadir confianza si el modelo la proporciona.</td></tr>
<tr><td>Validaciones</td><td>Mensajes claros para texto vacío, fallo al cargar el modelo o error de procesamiento.</td></tr></table>
<h2>Pruebas mínimas propuestas</h2>
<p><b>1.</b> Un texto nuevo por categoría: guardar resultado esperado y obtenido.<br><b>2.</b> Texto vacío: debe pedir contenido.<br><b>3.</b> Texto ambiguo: revisar la respuesta con una persona.<br><b>4.</b> Fallo del procesamiento: comprobar el mensaje de error.</p>
<h2>Qué entregar</h2>
<p><b>Código actualizado</b> de la interfaz y su conexión al procesamiento.</p>
<p><b>Evidencias de comunicación real:</b> capturas de entrada y respuesta, acompañadas de un registro de ejecución del backend.</p>
<p><b>Tabla de pruebas:</b> caso, resultado esperado, resultado obtenido, estado y errores o ajustes pendientes.</p>
<p class="nota"><b>Falta construir:</b> no se encontró aplicación ni evidencia de integración. La respuesta debe venir del modelo; la guía no acepta resultados simulados. Para esta propuesta basta ingresar texto: cargar PDF no es obligatorio.</p>
''')]

doc = pymupdf.open()
for i, (label, title, body) in enumerate(PAGES, 1):
    page = doc.new_page(width=595, height=842)
    html = f'<p style="color:#567386;font-size:10pt">{label.upper()} · SOLUCIÓN PROPUESTA</p><h1>{title}</h1>{body}'
    spare, scale = page.insert_htmlbox(pymupdf.Rect(40, 30, 555, 793), html, css=CSS, scale_low=1)
    assert spare >= 0, f'Contenido excede la página {i}'
    page.insert_text((40, 819), f'Resumen de los archivos de la carpeta | {i}/3', fontsize=8)
target = BASE / 'Soluciones_laboratorios_resumen.pdf'
doc.save(target)
doc.close()
with pymupdf.open(target) as check:
    assert len(check) == 3
    for i, page in enumerate(check, 1):
        text = page.get_text()
        assert '?' not in text and '\ufffd' not in text, f'Texto corrupto en página {i}'
        page.get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(BASE / f'revision_pagina_{i}.png')
    assert 'jurídicos' in check[0].get_text()
    assert 'Mínimo vital' in check[1].get_text()
print('PDF corregido: 3 páginas. Tildes, eñes y símbolos verificados.')
