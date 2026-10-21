"""Documentos sintéticos variados para probar el gestor web; no radica datos."""
from pathlib import Path
from html import escape
import csv
import pymupdf

BASE = Path(__file__).resolve().parent
# Orden mezclado para probar la identificación del tipo documental.
CASOS = [
    ('01_documento', 'Derecho de petición', 'Solicitud de información sobre obras del barrio',
     'Secretaría ficticia de Infraestructura', 'Peticionario: Persona ficticia A',
     'Presento derecho de petición de información y copia de documentos.',
     ['En el barrio ficticio Los Almendros se anunció una intervención de las vías peatonales. Los avisos instalados no permiten conocer el cronograma ni las condiciones de ejecución.',
      'La comunidad requiere información para organizar el acceso a sus viviendas. No solicito que un juez decida un conflicto ni presento una acción judicial.'],
     [('Peticiones', 'Solicito informar el cronograma previsto, identificar la dependencia responsable y entregar copia de los documentos públicos que describan el alcance de la obra. Pido explicar las medidas de acceso peatonal y el canal para reportar novedades.'),
      ('Respuesta y documentos', 'Solicito una respuesta clara a cada punto y el envío de la información por el mismo canal de presentación. Si algún documento tiene reserva, pido que se indique la razón y se facilite la parte pública disponible.')]),
    ('02_documento', 'Acción de tutela', 'Protección por interrupción de un tratamiento',
     'Señor(a) juez(a) de tutela — Reparto', 'Accionante: Persona ficticia B · Accionada: Entidad ficticia Salud Serena',
     'Interpongo acción de tutela para la protección de mis derechos fundamentales a la salud y a la vida digna.',
     ['Recibo tratamiento médico continuo y cuento con una orden vigente de entrega de medicamentos. La entidad suspendió el suministro sin ofrecer una alternativa que garantice su continuidad.',
      'Presenté una solicitud de solución y adjunté el soporte de la prescripción. La interrupción persiste y compromete mi recuperación. La petición previa se menciona como antecedente; este escrito solicita protección judicial.'],
     [('Derechos y pretensiones', 'Solicito amparar mis derechos fundamentales a la salud y a la vida digna. Pido ordenar la valoración de la situación y garantizar la continuidad del tratamiento prescrito, de acuerdo con la indicación del personal médico.'),
      ('Soportes del ejercicio', 'En este caso simulado se supone la existencia de la orden médica, la constancia de la solicitud previa y la respuesta recibida. No se aportan historias clínicas ni datos reales.')]),
    ('03_documento', 'Demanda', 'Incumplimiento de contrato de fabricación de muebles',
     'Señor(a) juez(a) competente — Reparto', 'Demandante: Persona ficticia C · Demandada: Empresa ficticia Madera Azul',
     'Presento demanda de naturaleza contractual por incumplimiento de las obligaciones pactadas.',
     ['Celebré un contrato para fabricar e instalar muebles de una oficina y entregué un anticipo ficticio de ocho millones de pesos. El plazo acordado venció sin que se realizara la instalación.',
      'Requerí a la empresa para obtener el cumplimiento o la devolución del anticipo. Las gestiones previas no resolvieron la controversia. El documento plantea un litigio contractual y no una solicitud de amparo constitucional.'],
     [('Pretensiones', 'Solicito declarar el incumplimiento contractual y disponer la resolución del contrato, la restitución del anticipo y los perjuicios que resulten probados. Pido resolver las costas según corresponda.'),
      ('Pruebas y trámite', 'Solicito valorar el contrato, los comprobantes del pago y las comunicaciones de requerimiento, supuestos para este ejercicio. La competencia, el procedimiento y los requisitos previos deberán verificarse en un caso real.')]),
    ('04_documento', 'Derecho de petición', 'Corrección de un registro de asistencia a capacitación',
     'Dirección ficticia de Formación Ciudadana', 'Peticionaria: Persona ficticia D',
     'Formulo derecho de petición de interés particular para solicitar la revisión de un registro administrativo.',
     ['Asistí a una capacitación organizada por la entidad y firmé el listado de asistencia. Al consultar el portal encontré que mi participación figura como incompleta.',
      'El registro impide descargar la constancia de participación. Cuento con el comprobante de inscripción y una copia del registro de ingreso que permiten revisar la novedad.'],
     [('Solicitudes', 'Solicito verificar el registro de asistencia, corregir la información si se acredita el error y habilitar la descarga de la constancia. Si consideran que falta un requisito, pido que se precise cuál y cómo puedo subsanarlo.'),
      ('Anexos y respuesta', 'Para la simulación se relacionan un comprobante de inscripción y un registro de ingreso. Pido una respuesta de fondo a cada solicitud a través del canal de recepción. No presento demanda ni solicito una orden judicial.')]),
    ('05_documento', 'Demanda', 'Reconocimiento de relación laboral y prestaciones',
     'Señor(a) juez(a) laboral competente — Reparto', 'Demandante: Persona ficticia E · Demandada: Empresa ficticia Taller Nube',
     'Promuevo demanda ordinaria laboral para discutir la existencia de una relación de trabajo y sus consecuencias económicas.',
     ['Durante dieciocho meses realicé labores de recepción siguiendo un horario y las instrucciones del supervisor. Recibía pagos mensuales y debía solicitar autorización para ausentarme.',
      'La empresa denominó el vínculo como prestación de servicios. Al finalizar no reconoció las prestaciones que considero derivadas de la relación laboral. Busco una decisión del juez sobre estas obligaciones.'],
     [('Pretensiones declarativas y de condena', 'Solicito declarar la existencia de una relación laboral durante el período que se acredite. Pido el reconocimiento y pago de las prestaciones, aportes y demás conceptos que se prueben en el proceso.'),
      ('Medios de prueba', 'Propongo valorar comunicaciones de instrucciones, registros de horario y comprobantes de pago, todos supuestos en este ejercicio. La demanda busca un pronunciamiento laboral ordinario, no el amparo urgente de una tutela.')]),
    ('06_documento', 'Acción de tutela', 'Acceso por mérito a un cargo público',
     'Señor(a) juez(a) de tutela — Reparto', 'Accionante: Persona ficticia F · Accionada: Entidad ficticia Puerto Claro',
     'Presento acción de tutela para la protección de mis derechos fundamentales a la igualdad, al debido proceso y al acceso a cargos públicos.',
     ['Participé en un concurso de méritos y obtuve el primer lugar en una lista de elegibles. La entidad anunció una vacante definitiva, pero no explicó por qué omitió considerar mi posición.',
      'Solicité revisar la actuación y recibí una respuesta que no examinó mi situación. En este supuesto académico planteo la necesidad de protección judicial por la afectación concreta de mis derechos.'],
     [('Solicitud de amparo', 'Pido amparar los derechos invocados y ordenar una revisión motivada de mi situación en el concurso. Solicito que se respete el orden de mérito y se adopte la decisión correspondiente según las reglas de la convocatoria.'),
      ('Antecedentes y soportes', 'Se supone la existencia de la convocatoria, la lista de elegibles y la comunicación presentada a la entidad. La procedencia del amparo y los demás medios de defensa requerirían valoración en un asunto real.')]),
    ('07_documento', 'Derecho de petición', 'Explicación de un cobro de servicio público',
     'Empresa ficticia Aguas del Horizonte — Atención al usuario', 'Peticionario: Persona ficticia G',
     'En ejercicio del derecho de petición, solicito información y revisión de la facturación de mi servicio.',
     ['La factura más reciente incluye un consumo considerablemente mayor que el registrado en los meses anteriores. La vivienda conserva el mismo uso y no se me informó de una novedad en la lectura.',
      'Necesito conocer la lectura inicial y final del medidor, el cálculo aplicado y los conceptos que explican la diferencia. Quiero que la empresa revise la información y responda antes de definir otras actuaciones.'],
     [('Peticiones concretas', 'Solicito copia del registro de lecturas, explicación del cálculo del consumo y revisión de los valores cobrados. Si se encuentra un error, pido corregir la factura y comunicar de forma detallada el ajuste.'),
      ('Documentación y notificación', 'Para el ejercicio se supone una copia de la factura y del historial de consumos. Solicito que la respuesta se remita por el canal de recepción. Este escrito está dirigido al prestador del servicio y no a un despacho judicial.')]),
    ('08_documento', 'Acción de tutela', 'Falta de ingresos por suspensión de la mesada',
     'Señor(a) juez(a) de tutela — Reparto', 'Accionante: Persona ficticia H · Accionado: Fondo ficticio Vida Plena',
     'Interpongo acción de tutela para proteger mi mínimo vital y mi vida en condiciones dignas.',
     ['Mi pensión constituye el único ingreso del hogar. Hace tres meses se suspendió su pago por una actualización administrativa, aunque entregué los documentos requeridos.',
      'No tengo ahorros ni otra actividad remunerada. La falta de ingresos me impide cubrir alimentación, arriendo y medicamentos. He pedido resolver la suspensión y no he obtenido una solución efectiva.'],
     [('Pretensiones de amparo', 'Solicito proteger mi mínimo vital y disponer que se examine de forma inmediata la suspensión. Pido restablecer los pagos que correspondan para atender las necesidades básicas del hogar y evitar que continúe la afectación.'),
      ('Soportes del supuesto', 'Se relacionan como pruebas simuladas los comprobantes de pagos anteriores y la constancia de entrega de documentos. No se incluyen extractos, identificaciones ni información económica de personas reales.')]),
    ('09_documento', 'Demanda', 'Cobro de una obligación documentada en pagaré',
     'Señor(a) juez(a) competente — Reparto', 'Demandante: Persona ficticia I · Demandada: Persona ficticia J',
     'Presento demanda ejecutiva para solicitar el pago de una obligación dineraria que consta en un pagaré.',
     ['En este supuesto, la parte demandada suscribió un pagaré por un préstamo ficticio de doce millones de pesos. La fecha de vencimiento transcurrió sin que se efectuara el pago acordado.',
      'Realicé requerimientos de pago sin obtener cumplimiento. El documento base y las condiciones de exigibilidad se suponen disponibles para su revisión por el despacho.'],
     [('Pretensiones ejecutivas', 'Solicito librar mandamiento de pago por el capital que resulte exigible, los intereses que legalmente correspondan y las costas que se determinen. Pido continuar el trámite según la decisión judicial y las oportunidades de defensa de la parte demandada.'),
      ('Título y anexos', 'Se supone un pagaré y la documentación de la obligación para el ejercicio. La suficiencia del título, la liquidación y los requisitos de presentación deben verificarse en una controversia real. No se pretende obtener una respuesta administrativa ni un amparo constitucional.')]),
    ('10_documento', 'Acción de tutela', 'Falta de respuesta a una petición previa',
     'Señor(a) juez(a) de tutela — Reparto', 'Accionante: Persona ficticia K · Accionada: Oficina ficticia de Archivo',
     'Presento acción de tutela por la presunta vulneración de mi derecho fundamental de petición.',
     ['Presenté ante la oficina una solicitud de copia de un expediente administrativo y obtuve constancia de recepción. En este supuesto transcurrió el término aplicable sin respuesta ni comunicación de ampliación.',
      'He consultado el estado de la solicitud y únicamente recibo mensajes automáticos. Adjunto como antecedente la petición inicial, pero este nuevo escrito se dirige al juez para solicitar protección constitucional.'],
     [('Solicitud al juez', 'Solicito tutelar mi derecho fundamental de petición y ordenar a la entidad que emita y comunique una respuesta clara, congruente y de fondo a la solicitud pendiente. No pido que necesariamente se conceda lo solicitado, sino que exista una respuesta efectiva.'),
      ('Pruebas del caso académico', 'Se supone la existencia de la solicitud original, la constancia de recepción y las consultas posteriores. Este caso permite comprobar que mencionar un derecho de petición no convierte una acción de tutela en una petición administrativa.')]),
]

CSS = '''body{font-family:sans-serif;font-size:11pt;line-height:1.5;color:#30294e}
h1{font-size:22pt;color:#4938b6;margin:12px 0 6px}h2{font-size:12pt;color:#4938b6;margin:16px 0 6px}
p{margin:7px 0}.banner{background:#f0ebfb;color:#68548b;font-size:9pt;padding:10px}
.subtitle{font-size:12pt}.meta{font-size:10pt;color:#746782}.footer{font-size:8pt;color:#8b7a96;margin-top:18px}'''

def generar():
    filas = []
    for slug, tipo, asunto, destinatario, partes, apertura, hechos, secciones in CASOS:
        texto = f'<p class="banner">CASO FICTICIO · DOCUMENTO SINTÉTICO DE PRUEBA</p><h1>{escape(tipo)}</h1><p class="subtitle"><b>{escape(asunto)}</b></p><p class="meta">{escape(destinatario)}<br>{escape(partes)}<br>Referencia académica: {slug.upper()}</p><p>{escape(apertura)}</p><h2>Hechos y antecedentes</h2>'
        texto += ''.join(f'<p><b>{i}.</b> {escape(h)}</p>' for i, h in enumerate(hechos, 1))
        texto += ''.join(f'<h2>{escape(titulo)}</h2><p>{escape(contenido)}</p>' for titulo, contenido in secciones)
        texto += '<p class="footer">Especialización en Inteligencia Artificial en Derecho · Laboratorio 3<br>Material ficticio para probar carga, extracción y clasificación. No corresponde a personas, procesos ni documentos reales. No está preparado para radicación.</p>'
        with pymupdf.open() as doc:
            page = doc.new_page(width=595, height=842)
            spare, scale = page.insert_htmlbox(pymupdf.Rect(44, 34, 551, 802), texto, css=CSS, scale_low=0.9)
            assert spare >= 0, f'Contenido fuera de página: {slug}'
            doc.set_metadata({'title': asunto, 'author': 'Lexia - ejemplos académicos ficticios', 'subject': 'Prueba de clasificación documental'})
            doc.save(BASE / f'{slug}.pdf')
        with pymupdf.open(BASE / f'{slug}.pdf') as doc:
            extraido = ''.join(p.get_text() for p in doc)
            assert len(doc) == 1 and len(extraido.split()) >= 180, slug
            assert 'FICTICIO' in extraido and tipo in extraido and '\ufffd' not in extraido, slug
        filas.append({'archivo':f'{slug}.pdf','tipo_esperado':tipo,'asunto':asunto})
    with (BASE / 'resultados_esperados.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['archivo', 'tipo_esperado', 'asunto'])
        writer.writeheader()
        writer.writerows(filas)
    print('Verificados: 10 PDF de una página, texto seleccionable y codificación correcta.')
    print('Distribución: 3 derechos de petición, 3 demandas, 4 acciones de tutela.')
    with pymupdf.open(BASE / '10_documento.pdf') as doc:
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(BASE / 'revision_documento_10.png')

if __name__ == '__main__':
    generar()
