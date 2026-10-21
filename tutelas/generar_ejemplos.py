"""Genera diez tutelas ficticias para pruebas de carga y clasificación."""
from pathlib import Path
import html
import pymupdf

BASE = Path(__file__).resolve().parent
CASOS = [
    ('01_reintegro_embarazo', 'Reintegro por desvinculación durante el embarazo', 'Derecho al trabajo',
     'Persona ficticia A', 'Empresa ficticia Aurora',
     ['Durante dos años presté servicios como auxiliar de inventarios mediante contrato de trabajo. Informé al empleador mi estado de embarazo y entregué una constancia médica.',
      'Dos semanas después recibí una comunicación que daba por terminado el vínculo laboral por una supuesta reorganización. No se me explicó si existía autorización de la autoridad competente.',
      'Mi pretensión principal es recuperar el empleo y mantener la continuidad de mi afiliación a la seguridad social durante la gestación.'],
     'Solicito el amparo de mis derechos al trabajo y a la estabilidad laboral reforzada. Pido que se examine la desvinculación, se ordene el reintegro que corresponda y se garantice la continuidad de la afiliación a la seguridad social.'),
    ('02_estabilidad_tratamiento_medico', 'Estabilidad laboral durante tratamiento médico', 'Derecho al trabajo',
     'Persona ficticia B', 'Empresa ficticia Horizonte',
     ['Trabajo como operario de empaque y estoy en tratamiento por una lesión de hombro. El área de personal recibió mis incapacidades y las recomendaciones para ajustar mis labores.',
      'Al regresar de una incapacidad fui retirado del cargo. La empresa indicó que mi rendimiento no era suficiente, aunque no había evaluado las recomendaciones de salud ocupacional.',
      'Solicité reconsiderar la decisión y asignarme tareas compatibles con mis restricciones, pero recibí una respuesta negativa.'],
     'Solicito proteger mis derechos al trabajo, a la estabilidad laboral reforzada y a la salud. Mi petición principal es el reintegro o la reubicación laboral compatible con las recomendaciones médicas, previa valoración del caso.'),
    ('03_libertad_sindical', 'Desvinculación posterior a actividad sindical', 'Derecho al trabajo',
     'Persona ficticia C', 'Empresa ficticia Sendero',
     ['Me desempeñaba como técnico de mantenimiento y participé en la creación de una organización sindical. La empresa fue informada de mi participación en las actividades de representación de trabajadores.',
      'Después de presentar una solicitud colectiva de mejoras en seguridad, fui excluido de los turnos y recibí una carta de terminación del contrato.',
      'Considero que existe relación entre la medida y mi actividad sindical. Aporto para este caso simulado comunicaciones internas y la cronología de los hechos.'],
     'Pido proteger mis derechos de asociación sindical y trabajo. Solicito revisar la desvinculación, cesar las conductas de represalia que se acrediten y disponer el restablecimiento del vínculo laboral si resulta procedente.'),
    ('04_reubicacion_discapacidad', 'Solicitud de ajustes y reubicación laboral', 'Derecho al trabajo',
     'Persona ficticia D', 'Empresa ficticia Prisma',
     ['Soy analista de soporte y tengo una limitación de movilidad que comuniqué al empleador. El puesto fue trasladado a un espacio al que solo se accede por escaleras.',
      'Pedí un ajuste del lugar de trabajo o una modalidad remota para continuar desempeñando mis funciones. La empresa negó ambas alternativas sin evaluar mis necesidades particulares.',
      'Posteriormente se me informó que, si no acudía al nuevo puesto, se consideraría que abandoné mis funciones. Deseo conservar mi empleo con condiciones de acceso adecuadas.'],
     'Solicito el amparo de mis derechos a la igualdad, al trabajo y a la inclusión. Pido que se valoren ajustes razonables y una reubicación accesible que me permitan continuar desempeñando mis funciones.'),
    ('05_mesadas_pensionales', 'Suspensión de la única mesada pensional', 'Mínimo vital',
     'Persona ficticia E', 'Fondo ficticio Amanecer',
     ['Soy una persona mayor y mi mesada pensional es la única fuente de recursos de mi hogar. Desde hace tres meses no recibo el pago por una supuesta actualización de datos.',
      'Entregué los documentos solicitados y pedí una respuesta, pero el trámite sigue pendiente. No tengo ahorros ni otra fuente de ingresos.',
      'He dejado de comprar alimentos suficientes y medicamentos de uso habitual. La situación también afecta el pago de los servicios básicos de mi vivienda.'],
     'Solicito proteger mi mínimo vital y mi vida digna. Pido resolver la suspensión y restablecer el pago de la pensión, con las sumas pendientes que correspondan, para atender mis necesidades básicas.'),
    ('06_incapacidades_sin_pago', 'Incapacidades pendientes y falta de recursos', 'Mínimo vital',
     'Persona ficticia F', 'Entidad ficticia Bienestar',
     ['Una intervención médica me impidió trabajar durante varias semanas. Presenté las incapacidades y los soportes requeridos para obtener la prestación económica correspondiente.',
      'Los pagos continúan pendientes y la entidad no ha indicado con claridad qué documento falta. Actualmente no cuento con ingresos adicionales.',
      'Tengo a cargo una persona dependiente y no puedo cubrir el mercado ni el arriendo. Mi solicitud se centra en obtener recursos indispensables para la subsistencia durante la recuperación.'],
     'Pido el amparo de mi mínimo vital y de una vida en condiciones dignas. Solicito resolver el trámite y reconocer y pagar las incapacidades que correspondan, evitando una interrupción injustificada de mis recursos de subsistencia.'),
    ('07_salarios_subsistencia', 'Salarios adeudados que comprometen la alimentación', 'Mínimo vital',
     'Persona ficticia G', 'Empresa ficticia Roble',
     ['Continúo vinculado como auxiliar de cocina, pero no he recibido el salario de los dos últimos meses. Es el único ingreso de mi hogar.',
      'He solicitado el pago en varias oportunidades. La empresa anuncia nuevas fechas y no cumple los compromisos, aunque sigo prestando mis servicios.',
      'Ya no dispongo de dinero para alimentos y debo parte del arriendo. Mi petición urgente es recuperar los recursos de subsistencia; no estoy solicitando un reintegro porque conservo el empleo.'],
     'Solicito proteger mi mínimo vital y el de mi hogar. Pido que se examine la falta de pago y se adopten las medidas que procedan para garantizar los salarios adeudados y atender mis necesidades básicas.'),
    ('08_lista_elegibles', 'Nombramiento pendiente de una lista de elegibles', 'Meritocracia',
     'Persona ficticia H', 'Entidad ficticia Valle Claro',
     ['Participé en un concurso de méritos para un cargo público y obtuve el primer lugar en la lista de elegibles. El proceso y la lista se encuentran definidos en este supuesto académico.',
      'La entidad informó que existe una vacante definitiva, pero no ha efectuado mi nombramiento ni ha explicado las razones de la demora.',
      'Presenté una solicitud para que se respetara el orden de mérito. Recibí una respuesta general que no resolvió la situación concreta.'],
     'Solicito proteger mis derechos de acceso a cargos públicos, igualdad y debido proceso. Pido que se evalúe mi situación y se respete el orden de la lista de elegibles al proveer la vacante conforme a las reglas de la convocatoria.'),
    ('09_exclusion_concurso', 'Exclusión de concurso por un soporte no valorado', 'Meritocracia',
     'Persona ficticia I', 'Organizador ficticio Mérito Abierto',
     ['Me inscribí en una convocatoria pública y cargué los documentos de formación y experiencia antes del cierre. Conservo la constancia de recepción de los archivos.',
      'En la etapa de verificación fui excluido por ausencia de un certificado que sí aparece en la constancia. Presenté reclamación con la evidencia de la carga oportuna.',
      'La respuesta mantuvo la exclusión sin analizar el certificado ni explicar por qué no fue valorado. La siguiente fase del concurso está próxima a comenzar.'],
     'Pido proteger mis derechos al debido proceso, a la igualdad y al acceso a cargos públicos. Solicito una revisión motivada de los documentos presentados oportunamente y de mi permanencia en el concurso de méritos.'),
    ('10_puntaje_experiencia', 'Reclamación por valoración de experiencia en concurso', 'Meritocracia',
     'Persona ficticia J', 'Comisión ficticia Servicio Transparente',
     ['Participé en un concurso para un empleo público. En la valoración de antecedentes se omitió una certificación de experiencia aportada dentro del plazo establecido.',
      'La omisión modificó mi puntaje y mi posición frente a las demás personas aspirantes. Solicité conocer el criterio utilizado y el detalle de la calificación.',
      'La respuesta reprodujo el puntaje inicial sin pronunciarse sobre la certificación cuestionada. Solicito una evaluación conforme a las mismas reglas aplicadas a los demás participantes.'],
     'Solicito proteger mis derechos a la igualdad, al debido proceso y al acceso por mérito a cargos públicos. Pido revisar la valoración de experiencia, responder de forma motivada mi reclamación y ajustar el puntaje y el orden de mérito si corresponde.'),
]

CSS = '''body{font-family:sans-serif;font-size:11pt;color:#29264b;line-height:1.55}
h1{font-size:21pt;color:#4938b6;margin:8px 0 16px}h2{font-size:12pt;color:#4938b6;margin-top:18px}
p{margin:8px 0}.badge{font-size:9pt;color:#68538b;background:#f1ecfa;padding:10px}
.meta{font-size:10pt;color:#62596f}.footer{font-size:8.5pt;color:#786c88;margin-top:20px}'''

def generar():
    for slug, titulo, categoria, actor, demandado, hechos, pretension in CASOS:
        cuerpo = ''.join(f'<p><b>{i}.</b> {html.escape(h)}</p>' for i, h in enumerate(hechos, 1))
        contenido = f'''<p class="badge">MATERIAL DE PRUEBA · CASO COMPLETAMENTE FICTICIO</p>
<h1>Acción de tutela</h1><p><b>{html.escape(titulo)}</b></p>
<p class="meta">Señor(a) juez(a) de tutela — Reparto<br>
Accionante: {actor}<br>Accionado: {demandado}<br>
Asunto: solicitud de protección de derechos fundamentales</p>
<h2>I. Hechos</h2>{cuerpo}
<h2>II. Solicitud de protección</h2><p>{html.escape(pretension)}</p>
<h2>III. Soportes del caso simulado</h2><p>Para el ejercicio se supone la existencia de comunicaciones y solicitudes previas relacionadas con los hechos. No se adjuntan pruebas reales ni datos de personas.</p>
<p class="footer">Especialización en Inteligencia Artificial en Derecho · Laboratorio 3<br>
Documento sintético para probar carga, extracción y clasificación. No corresponde a un proceso real ni está preparado para radicación.</p>'''
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)
        spare, _ = page.insert_htmlbox(pymupdf.Rect(44, 35, 551, 802), contenido, css=CSS, scale_low=0.85)
        assert spare >= 0, f'Contenido fuera de página: {slug}'
        doc.set_metadata({'title': titulo, 'author': 'Lexia - material ficticio de prueba', 'subject': 'Tutela sintética para laboratorio académico'})
        doc.save(BASE / f'{slug}.pdf')
        doc.close()
    for ruta in BASE.glob('*.pdf'):
        with pymupdf.open(ruta) as doc:
            texto = ''.join(p.get_text() for p in doc)
            assert len(texto.split()) >= 150, ruta.name
            assert 'FICTICIO' in texto, ruta.name
            assert '\ufffd' not in texto, ruta.name
    assert len(list(BASE.glob('*.pdf'))) == 10
    print('Verificados: 10 PDF legibles, con texto seleccionable y casos ficticios.')

if __name__ == '__main__':
    generar()
