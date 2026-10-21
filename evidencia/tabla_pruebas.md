# Tabla de pruebas de integración

Ejecutada: 2026-10-21 17:40:47 · 28/28 casos pasan

| # | Caso | Resultado esperado | Resultado obtenido | Estado | Errores / pendientes |
|---|---|---|---|---|---|
| 1 | Salud del backend | HTTP 200 y los 3 modelos cargados | HTTP 200: modelo_ok=True, modelos=['rama', 'tema', 'tipo'] | PASA |  |
| 2 | Tutela nueva sobre trabajo | Tutela · asunto Derecho al trabajo | HTTP 200: Tutela (62%) · rama Derecho laboral (83%) · asunto Derecho al trabajo · estado «Clasificado» | PASA |  |
| 3 | Tutela nueva sobre mínimo vital | Tutela · asunto Mínimo vital | HTTP 200: Tutela (72%) · rama Derecho laboral (69%) · asunto Mínimo vital · estado «Clasificado» | PASA |  |
| 4 | Tutela nueva sobre meritocracia | Tutela · asunto Meritocracia | HTTP 200: Tutela (61%) · rama Derecho administrativo (71%) · asunto Meritocracia · estado «Clasificado» | PASA |  |
| 5 | Derecho de petición nuevo | Derecho de petición · sin asunto de tutela | HTTP 200: Derecho de petición (84%) · rama Derecho administrativo (54%) · asunto — · estado «Clasificado» | PASA |  |
| 6 | Demanda nueva (ejecutiva) | Demanda · rama Derecho civil · sin asunto | HTTP 200: Demanda (90%) · rama Derecho civil (58%) · asunto — · estado «Clasificado» | PASA |  |
| 7 | Tutela de salud (fuera de las 3 categorías del Lab 2) | Se clasifica como Tutela y se deja el asunto a revisión humana | HTTP 200: Tutela, asunto forzado a «Derecho al trabajo» (44%), estado «Requiere revisión» | PASA | Limitación: el Lab 2 no tiene la categoría «Salud»; una persona debe revisar el asunto |
| 8 | Texto ambiguo | HTTP 200; si la confianza < 55 % queda «Requiere revisión» | HTTP 200: Tutela (41%), estado «Requiere revisión» | PASA | Un humano debe revisar este caso (texto ambiguo a propósito) |
| 9 | Texto vacío | HTTP 400 y mensaje que pide contenido | HTTP 400: El texto está vacío. Pega el contenido del documento o sube un archivo. | PASA |  |
| 10 | Texto demasiado corto | HTTP 400 (mínimo 40 caracteres) | HTTP 400: El texto es muy corto (20 caracteres). Escribe al menos 40. | PASA |  |
| 11 | Archivo PDF con texto | Tutela · asunto Derecho al trabajo | HTTP 200: Tutela (62%) · rama Derecho laboral (83%) · asunto Derecho al trabajo · estado «Clasificado» | PASA |  |
| 12 | Archivo Word (.docx) | Derecho de petición | HTTP 200: Derecho de petición (84%) · rama Derecho administrativo (54%) · asunto — · estado «Clasificado» | PASA |  |
| 13 | Archivo de texto (.txt) | Demanda | HTTP 200: Demanda (90%) · rama Derecho civil (58%) · asunto — · estado «Clasificado» | PASA |  |
| 14 | Word antiguo (.doc) | HTTP 422 y pide convertir a .docx | HTTP 422: El formato .doc (Word antiguo) no se puede leer. Ábrelo y guárdalo como .docx o PDF. | PASA |  |
| 15 | PDF escaneado sin texto | HTTP 422 y explica que no hay texto/OCR | HTTP 422: El PDF no tiene texto seleccionable (probablemente es un escaneo). Esta versión no aplica OCR: sube una versión con texto o pega el contenido. | PASA |  |
| 16 | Formato no soportado (.exe) | HTTP 422 y lista de formatos | HTTP 422: Formato '.exe' no soportado. Usa PDF, Word (.docx), .odt, .rtf o .txt. | PASA |  |
| 17 | Lote de 3 archivos con uno inválido | Procesa los válidos y reporta el inválido | HTTP 200: resultados por archivo = [True, False, True] | PASA |  |
| 18 | Corrección humana de categoría y estado | Se guarda y queda en el historial | HTTP 200: categoría=Demanda, estado=En revisión, corregido=True | PASA |  |
| 19 | Corrección humana del asunto de la tutela | Se guarda, conserva lo que propuso el modelo y queda en el historial | HTTP 200: asunto Derecho al trabajo → Mínimo vital; el modelo propuso Derecho al trabajo | PASA |  |
| 20 | Asunto de tutela en un documento que no es tutela | HTTP 400 con mensaje claro | HTTP 400: El asunto de la tutela solo aplica a documentos de tipo Tutela. | PASA |  |
| 21 | Guardar una revisión sin indicar quién revisó | HTTP 400 que pide al menos un revisor del equipo | HTTP 400: Indica quién revisó el documento (al menos una persona del equipo) para guardar los cambios. | PASA |  |
| 22 | Revisor que no pertenece al equipo | HTTP 400 (solo se aceptan los integrantes de la lista) | HTTP 400: Revisor no válido: elige integrantes de la lista del equipo. | PASA |  |
| 23 | Ficha PDF del expediente con los revisores | PDF válido que contiene el nombre de cada persona que revisó | PDF de 102 KB; incluye los nombres de los revisores: True | PASA |  |
| 24 | Bandeja filtrada por revisor | Solo expedientes revisados por esa persona | HTTP 200: 1 expedientes revisados por Willigton Herrera | PASA |  |
| 25 | Estado inválido | HTTP 400 | HTTP 400: Estado no válido. | PASA |  |
| 26 | Expediente inexistente | HTTP 404 con mensaje | HTTP 404: El documento no existe. | PASA |  |
| 27 | Fallo de carga del modelo | HTTP 503 con mensaje claro | HTTP 503: No existe el modelo «tipo» (modelo_tipo.joblib). Ejecuta: python backend/entrenar.py | PASA |  |
| 28 | Bandeja filtrada por categoría | Solo expedientes de la categoría pedida | HTTP 200: 10 expedientes de Tutela en la bandeja | PASA |  |
