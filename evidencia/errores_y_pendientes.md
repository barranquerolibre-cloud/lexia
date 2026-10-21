# Errores encontrados y pendientes (Laboratorio 3)

## Errores encontrados durante la integración

| # | Qué pasó | Cómo se detectó | Ajuste |
|---|---|---|---|
| 1 | La prueba «corrección humana» fallaba: la categoría elegida coincidía con la que ya había propuesto el modelo, así que no había cambio | Prueba automática (`pruebas/pruebas.py`) | La prueba ahora elige siempre una categoría distinta a la del modelo |
| 2 | El expediente mostraba el texto «null» en el panel de clasificación (`replaceChildren` convierte `null` en texto) | Revisión visual de la captura del expediente | Se filtran los valores nulos en `web/documento.js`; la prueba de navegador vigila que no vuelva a aparecer |
| 3 | El PDF de prueba usaba una tutela de **salud**, y el modelo del Laboratorio 2 solo conoce trabajo, mínimo vital y meritocracia: forzó el asunto «Derecho al trabajo» con 44 % de confianza | Prueba automática | Se dejó como caso de prueba explícito (limitación conocida: queda en «Requiere revisión»); el PDF de prueba pasó a ser una tutela de trabajo |
| 4 | Un servidor viejo seguía abierto y mantenía la base de datos anterior con datos de ejemplo, por eso la bandeja no aparecía vacía | Reporte del usuario | Reiniciar el servidor y borrar `backend/gestor.db` |
| 5 | Las pruebas de navegador esperaban 3 barras de probabilidad y el historial «corregida»; la interfaz ya muestra 9 barras (tipo, rama y asunto) y el texto cambió a «corregido» | Prueba de navegador | Se actualizaron las expectativas de la prueba |

## Pendientes y limitaciones

- **Datasets sintéticos:** `datos/dataset.csv` (tipo de documento) y `datos/tutelas.csv` (Laboratorio 2) fueron creados para el laboratorio con ayuda de IA. Falta que el equipo los **revise y firme** (columna `revisado_por`). `datos/rama_derecho.csv` son los 120 textos del cuaderno del Laboratorio 1.
- **Exactitud optimista:** el modelo de asunto marca ≈99 % en validación cruzada porque los textos usan expresiones muy claras («mínimo vital», «reintegro», «lista de elegibles»). Con tutelas reales será menor. La rama del derecho rinde ≈80 %, igual que en el cuaderno del Laboratorio 1.
- **Asuntos limitados:** el modelo del Laboratorio 2 solo cubre tres asuntos. Una tutela sobre salud, educación u otro derecho se asigna igualmente a uno de los tres; por eso existe la revisión humana.
- **Sin OCR:** los PDF escaneados se rechazan con un mensaje claro.
- **`.doc` antiguo:** no se lee; hay que guardarlo como `.docx` o PDF.
- **Plazos:** días hábiles sin festivos. Tutela (10) y petición (15) deben confirmarse con la norma; el plazo de demanda (30) es una referencia interna, no un término legal.
- **Sin autenticación:** no usar con datos personales reales.
- **Evidencia propia:** las capturas y registros de `evidencia/` salieron de servidores de prueba. Para la entrega, repetir el flujo en el servidor del equipo (`python backend/app.py`) y tomar capturas nuevas; el registro real queda en `evidencia/registro_backend.log`.
- **Prueba con el backend apagado:** verificada en navegador automatizado; repetirla a mano antes de entregar.
