# Lexia · Gestor de tutelas, derechos de petición y demandas (Laboratorio 3)

Interfaz web conectada a un backend Flask con tres clasificadores reales (TF-IDF + regresión logística) que trabajan en cadena:

| Modelo | Categorías | Datos |
|---|---|---|
| Tipo de documento | Tutela · Derecho de petición · Demanda | `datos/dataset.csv` (sintético) |
| Rama del derecho (**Laboratorio 1**) | Laboral · Civil · Administrativo | `datos/rama_derecho.csv` (los 120 textos del cuaderno) |
| Asunto de la tutela (**Laboratorio 2**) | Derecho al trabajo · Mínimo vital · Meritocracia | `datos/tutelas.csv` (creado por el equipo con ayuda de IA; solo se aplica a tutelas) |

## Ejecutar

```sh
pip install -r backend/requirements.txt
python datos/generar_dataset.py      # tipo de documento (sintético, 71 fragmentos)
python datos/extraer_rama_derecho.py # Lab 1: 120 textos del cuaderno
python datos/generar_tutelas.py      # Lab 2: 72 fragmentos de tutelas por asunto
python backend/entrenar.py           # crea backend/modelo_tipo|rama|tema.joblib
python backend/app.py                # http://127.0.0.1:5000
```

Páginas: `/` Radicar · `/bandeja` · `/documento?id=N` · `/guia` (paso a paso de la tarea).

## Quién revisó

- Los integrantes están en `datos/integrantes.json` (fuente única). Los generadores reparten la columna `revisado_por` de `dataset.csv` y `tutelas.csv` entre ellos; cada persona debe revisar las filas que lleven su nombre.
- En la página, al guardar una revisión en el expediente hay que marcar quién revisó. El nombre queda en el historial, en la bandeja (columna y filtro «Revisado por») y en la **ficha PDF** del expediente.

## Despliegue en Render

1. Sube el proyecto a un repositorio de GitHub (mejor **privado**: `datos/integrantes.json` trae los nombres del equipo).
2. En Render: **New → Blueprint** y elige el repositorio. Lee `render.yaml`: instala dependencias, entrena los modelos (`python backend/entrenar.py`) y arranca con `gunicorn`.
3. Cuando termine el despliegue, abre la URL pública que da Render.

Detalles a tener en cuenta:
- En el plan gratis el servicio **se duerme** tras ~15 min sin uso (el primer clic tarda cerca de 1 min) y el disco es temporal: **la bandeja se vacía** al reiniciar o redesplegar. Para guardarla hace falta un disco persistente (plan de pago) o PostgreSQL.
- La aplicación no tiene login: cualquiera con el enlace puede ver y radicar. No uses datos reales.
- El build **no** regenera los CSV: se usan los de `datos/` tal como estén en el repositorio (incluidas las revisiones hechas a mano).
- `gunicorn` no corre en Windows: en local sigue siendo `python backend/app.py`.

## Estructura

| Ruta | Contenido |
|---|---|
| `web/` | Frontend (HTML, CSS, JS sin dependencias). `_mockup_original/` guarda el mockup anterior. |
| `backend/` | `app.py` (API), `modelo.py`, `entrenar.py`, `extraer.py` (PDF/Word/odt/rtf/txt), `db.py` (SQLite). |
| `datos/` | Scripts y CSV de los tres modelos. |
| `pruebas/` | `pruebas.py` (28 casos contra el backend real) y `e2e_ui.cjs` (navegador real). |
| `evidencia/` | Tabla de pruebas, registros del backend y capturas. |

## API

`GET /api/salud` · `GET /api/categorias` · `POST /api/documentos` (JSON `{texto, asunto}` o multipart `archivo`) ·
`GET /api/documentos` (filtros `categoria`, `rama`, `tema`, `estado`, `q`) · `GET|PUT /api/documentos/<id>` · `GET /api/documentos/<id>/ficha.pdf` · `GET /api/registro` · `GET /api/pruebas`

## Pruebas

```sh
python pruebas/pruebas.py     # genera evidencia/tabla_pruebas.md
node pruebas/e2e_ui.cjs       # requiere el backend en marcha y Playwright (web/.preview/node_modules)
```

## Límites conocidos

- Datasets de tipo y asunto sintéticos y pequeños: las exactitudes medidas (≈94 % tipo, ≈99 % asunto en validación cruzada) no se pueden extrapolar a documentos reales. La rama rinde ≈80 %, como en el cuaderno del Lab 1.
- El asunto solo cubre tres categorías: una tutela de salud u otro derecho se asigna igualmente a una de ellas; por eso hay revisión humana.
- Errores y pendientes: ver `evidencia/errores_y_pendientes.md`.
- Sin OCR: un PDF escaneado se rechaza con un mensaje. No se leen `.doc` antiguos.
- Plazos en días hábiles sin festivos; el de demanda es una referencia interna. Confírmalos con la norma.
- Sin autenticación: no usar con datos personales reales.
- La bandeja parte vacía: solo muestra documentos que radicas tú, clasificados por el modelo. No hay datos de ejemplo.
- Para entrenar con documentos reales, reemplaza los CSV de `datos/` (columnas `id,texto,categoria,origen,revisado_por`) por textos anonimizados y corre `python backend/entrenar.py`.
