# Documentos variados para probar la web

Selecciona los **10 archivos PDF** de esta carpeta para cargarlos juntos. Todos tienen texto seleccionable y contienen casos ficticios diferentes.

| Archivo | Tipo esperado | Asunto |
|---|---|---|
| 01_documento.pdf | Derecho de petición | Información sobre obras del barrio |
| 02_documento.pdf | Acción de tutela | Continuidad de tratamiento médico |
| 03_documento.pdf | Demanda | Incumplimiento de contrato de muebles |
| 04_documento.pdf | Derecho de petición | Corrección de registro de asistencia |
| 05_documento.pdf | Demanda | Reconocimiento de relación laboral |
| 06_documento.pdf | Acción de tutela | Acceso por mérito a cargo público |
| 07_documento.pdf | Derecho de petición | Revisión de factura de servicio público |
| 08_documento.pdf | Acción de tutela | Mínimo vital por suspensión de pensión |
| 09_documento.pdf | Demanda | Cobro ejecutivo de pagaré |
| 10_documento.pdf | Acción de tutela | Falta de respuesta a petición previa |

El caso 10 menciona una petición previa, pero el documento cargado es una tutela: permite revisar confusiones por palabras compartidas. Los nombres de archivo son neutros para que puedas observar la clasificación a partir del contenido.

Compara el resultado de la web con esta tabla o con `resultados_esperados.csv`. Los tipos son los esperados por el diseño de los ejemplos; no se ha medido aquí el acierto del modelo ni se han cargado documentos a la bandeja.

Los PDF son exclusivamente material académico ficticio, no escritos listos para radicación. Para regenerarlos: `python aleatorio/generar_documentos.py` (requiere PyMuPDF).
