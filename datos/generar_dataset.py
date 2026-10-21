"""Genera datos/dataset.csv: corpus SINTÉTICO de fragmentos jurídicos en español.

Tres categorías: Tutela, Derecho de petición, Demanda. Todos los textos fueron
redactados para este laboratorio (origen = sintetizado). No hay personas,
radicados ni entidades reales: se usan marcas como [NOMBRE] o [ENTIDAD].
Incluye casos fronterizos a propósito (marcados en `nota`) para estudiar errores.
"""
import csv
from pathlib import Path

from integrantes import revisor

TUTELA = [
    "Acudo a la acción de tutela para que se amparen mis derechos fundamentales a la salud y a la vida digna, vulnerados por la EPS [ENTIDAD], que se niega a autorizar la cirugía ordenada por mi médico tratante.",
    "Solicito al juez constitucional que tutele mi derecho fundamental al mínimo vital. Desde hace tres meses no recibo la mesada pensional, que es mi único ingreso, y no tengo cómo pagar el arriendo ni los alimentos.",
    "Instauro acción de tutela contra [ENTIDAD] por la vulneración del derecho al debido proceso. Pido que se ordene dejar sin efectos la decisión que me excluyó del concurso sin motivación alguna.",
    "Mi derecho a la educación está siendo vulnerado: la universidad no me permite matricularme por una deuda que ya fue refinanciada. Pido que mediante tutela se ordene mi inscripción de inmediato.",
    "Se trata de un perjuicio irremediable: mi hijo de cuatro años necesita el medicamento y la EPS lleva dos meses sin entregarlo. Solicito medida provisional y que se tutelen sus derechos a la salud y a la vida.",
    "El accionante afirma que fue despedido estando en tratamiento médico, sin autorización del Ministerio del Trabajo, por lo que invoca la estabilidad laboral reforzada y pide el reintegro por vía de tutela.",
    "Quedé en el primer lugar de la lista de elegibles y la entidad no me nombra pese a existir vacante. Presento acción de tutela para proteger mi derecho de acceso a cargos públicos y el debido proceso.",
    "Manifiesto bajo la gravedad del juramento que no he presentado otra tutela por los mismos hechos. Solicito que se ampare mi derecho fundamental a la dignidad humana y se ordene a la accionada cesar la vulneración.",
    "Pretensiones: PRIMERA. Tutelar los derechos fundamentales a la salud, a la seguridad social y a la vida en condiciones dignas. SEGUNDA. Ordenar a la EPS autorizar y practicar el procedimiento en un término de cuarenta y ocho horas.",
    "Soy una persona de la tercera edad, sujeto de especial protección constitucional. El fondo de pensiones negó mi sustitución pensional y eso afecta mi mínimo vital; por eso acudo a la tutela como mecanismo transitorio.",
    "El juez de primera instancia debe analizar si se cumple el requisito de subsidiariedad: la actora no cuenta con otro medio de defensa idóneo y enfrenta un daño inminente que exige protección inmediata.",
    "Señor juez: escribo porque me quitaron el subsidio y mi familia se está quedando sin comida. Creo que me están violando derechos fundamentales y quiero que me protejan con una tutela lo más pronto posible.",
    "La accionada vulneró el derecho a la igualdad al negarse a reconocer a mi pareja del mismo sexo como beneficiaria del servicio de salud. Solicito el amparo constitucional y que se ordene su afiliación.",
    "Ejerzo la acción de tutela porque la autoridad de tránsito retuvo mi vehículo de trabajo y con ello me privó de mi única fuente de ingresos, afectando mi derecho al trabajo y al mínimo vital.",
    "La Corte Constitucional ha señalado que la tutela procede de manera excepcional cuando se afectan derechos fundamentales y no existe otro mecanismo eficaz. En este caso, el menor requiere atención inmediata.",
    "Interpongo tutela contra la decisión de la junta de calificación, pues desconoció mi derecho fundamental a la seguridad social al negarme la pérdida de capacidad laboral sin valorar mis exámenes.",
    "Los hechos son los siguientes: 1. Estoy afiliada a la EPS desde hace diez años. 2. Me diagnosticaron una enfermedad huérfana. 3. La EPS niega el tratamiento. Por ello pido el amparo de mi derecho a la salud.",
    "El peticionario, persona en situación de discapacidad, fue desalojado sin orden judicial. Se solicita al juez de tutela proteger su derecho a la vivienda digna y ordenar su reubicación mientras se resuelve el caso.",
    "Acción de tutela por vulneración del derecho al habeas data: la central de riesgo mantiene un reporte negativo caducado y se niega a eliminarlo. Pido que se ordene su retiro y se proteja mi buen nombre.",
    "Presento tutela porque el colegio me negó el cupo escolar a mi hija por no tener los documentos de residencia, desconociendo su derecho fundamental a la educación. Pido que se ordene matricularla de inmediato.",
    "Hice una solicitud a la entidad hace seis meses y nunca respondió; por eso, además de acudir a la acción de tutela, pido que se proteja mi derecho fundamental de petición y se ordene una respuesta de fondo.",
    "Se solicita medida provisional urgente: la paciente está hospitalizada, el hospital se niega a continuar el tratamiento por falta de pago de la EPS y su vida corre peligro. Se invoca la tutela para evitar un perjuicio irremediable.",
    "El señor [NOMBRE] actúa por intermedio de agente oficioso porque su padre no está en condiciones de promover directamente la acción de tutela. Se vulneran sus derechos fundamentales a la salud y a la integridad personal.",
    "Contra el fallo de primera instancia que negó el amparo, impugno la decisión de tutela. El juez no valoró que el accionante carece de recursos y que está en riesgo su derecho fundamental a la vida digna.",
]

PETICION = [
    "En ejercicio del derecho de petición consagrado en el artículo 23 de la Constitución Política, solicito respetuosamente que se me expida copia de la resolución que aprobó mi traslado, junto con sus anexos.",
    "Por medio de la presente me permito solicitar información sobre el estado de mi trámite de licencia de construcción, radicado hace dos meses, y el tiempo estimado de respuesta.",
    "Respetados señores: quisiera pedir una certificación laboral en la que consten mi cargo, el tiempo de servicio y el salario devengado. La necesito para presentarla ante una entidad financiera.",
    "Solicito se me informe cuántos subsidios de vivienda fueron asignados en el último año en el municipio, discriminados por barrio, y se me remita el acto administrativo que fijó los criterios.",
    "Con fundamento en el derecho de petición, requiero que la secretaría de movilidad me explique por qué razón se me impuso el comparendo y me envíe el video o la prueba que lo respalda.",
    "Buen día. Quiero que me envíen el paz y salvo de mi cuenta de servicios públicos, ya que cancelé la deuda el mes pasado y todavía me aparece como pendiente en la factura.",
    "Petición de consulta: solicito que la entidad indique cuál es el concepto jurídico vigente sobre la procedencia de la licencia de maternidad para trabajadoras independientes y las normas que lo sustentan.",
    "Me dirijo a ustedes para formular una queja por la demora en la atención en la ventanilla y pedir que se adopten medidas para mejorar el servicio, informándome de las acciones tomadas.",
    "Solicito que se corrija el error en mi nombre en el registro de la entidad, pues aparece escrito con una letra equivocada. Adjunto copia de mi documento de identidad para facilitar la corrección.",
    "En virtud del artículo 23 superior y de la ley que lo reglamenta, pido que se me conceda cita para la entrega de documentos y que se me indique la lista completa de requisitos para el trámite.",
    "Pido que se me entregue copia íntegra de mi historia laboral y del reporte de semanas cotizadas, con el fin de verificar los aportes que hizo mi empleador durante los últimos cinco años.",
    "Señores de la alcaldía: solicito que informen cuándo se va a reparar el alumbrado de la calle de mi barrio y qué dependencia es la responsable, porque llevamos meses con la vía a oscuras.",
    "Mediante este escrito solicito la actualización de mis datos de contacto en el sistema y que las notificaciones se envíen únicamente a mi correo electrónico, que informo al final de esta comunicación.",
    "Derecho de petición dirigido a [ENTIDAD]: requiero que se me suministre el listado de contratos suscritos en el 2025, con su objeto, valor y contratista, en virtud del principio de transparencia.",
    "Cordial saludo. Necesito saber si mi solicitud de devolución del saldo a favor ya fue aprobada y, de ser así, la fecha en que se hará el pago. Agradezco una respuesta clara y de fondo.",
    "Solicito respetuosamente prórroga del plazo para presentar los documentos faltantes de mi inscripción, ya que por motivos de salud no pude reunirlos en el término inicial.",
    "Elevo petición para que me indiquen el procedimiento para solicitar la exención del impuesto predial por tratarse de mi única vivienda, los formularios necesarios y el plazo para presentarlos.",
    "De manera atenta solicito el desglose de los valores cobrados en mi factura, pues el monto aumentó sin explicación. Pido que se envíe la respuesta dentro del término legal de quince días hábiles.",
    "Quiero preguntar si el certificado de antecedentes que expidieron tiene vigencia indefinida o si debo renovarlo, y en qué oficina puedo hacerlo. Gracias de antemano por su pronta respuesta.",
    "Solicito la revocatoria del cobro de la cuota de administración que se me aplicó por error y que se me indique el procedimiento para pedir la devolución de lo pagado de más.",
    "En ejercicio del derecho de petición, requiero a la oficina de personal que certifique si tengo vacaciones pendientes y que me comunique el número de días acumulados a la fecha.",
    "Mediante el presente derecho de petición pido que me informen el estado de la queja que radiqué el año pasado ante la entidad, y que me remitan copia del expediente y de las actuaciones realizadas.",
    "Solicito a la Superintendencia que me indique si la empresa [ENTIDAD] se encuentra vigilada por ellos, y que me envíe el reglamento que consagra los derechos de los usuarios frente al servicio.",
    "Atentamente pido me sea enviada, por medio electrónico, la constancia de que radiqué el recurso en la fecha señalada, ya que no recibí ningún comprobante al momento de entregarlo.",
]

DEMANDA = [
    "DEMANDANTE: [NOMBRE]. DEMANDADO: [NOMBRE]. Pretensiones: Primera. Que se declare resuelto el contrato de compraventa del vehículo por incumplimiento del vendedor. Segunda. Que se condene al pago de los perjuicios, estimados bajo juramento en veinte millones de pesos.",
    "Señor Juez Civil del Circuito: actuando mediante apoderado judicial, presento demanda ejecutiva en contra del deudor para obtener el pago del pagaré vencido, más los intereses moratorios causados desde la fecha de exigibilidad.",
    "Hechos: 1. Las partes celebraron contrato de arrendamiento el 1 de marzo. 2. El arrendatario dejó de pagar el canon desde junio. 3. Se solicita la restitución del inmueble y la condena en costas al demandado.",
    "Con fundamento en los artículos 82 y siguientes del Código General del Proceso, presento demanda declarativa de responsabilidad civil extracontractual por los daños derivados del accidente de tránsito, cuantía de ciento cincuenta millones.",
    "Pretendo que se declare que he adquirido por prescripción extraordinaria el dominio del predio que poseo de manera pública, pacífica e ininterrumpida desde hace más de veinte años, y que se ordene su inscripción.",
    "Demanda de nulidad y restablecimiento del derecho contra la Resolución que me declaró insubsistente. Pedimos que se anule el acto, se ordene el reintegro y se paguen los salarios dejados de percibir desde el retiro.",
    "Competencia y cuantía: este despacho es competente por el lugar de cumplimiento de la obligación y por tratarse de un proceso de mayor cuantía. Se anexan como pruebas el contrato, los recibos y el certificado de existencia.",
    "Los herederos instauran demanda de sucesión intestada y piden la partición de los bienes dejados por el causante, así como el reconocimiento de la sociedad conyugal y la designación de un partidor.",
    "Presentamos demanda de divorcio por causal de separación de hecho, y solicitamos fijar la cuota alimentaria, regular las visitas del menor y liquidar la sociedad conyugal conforme a la ley.",
    "DEMANDA ORDINARIA LABORAL. El demandante prestó servicios a la sociedad demandada entre 2019 y 2024 sin que se le reconocieran prestaciones sociales. Se pide declarar la existencia del contrato de trabajo y condenar al pago de cesantías, primas y vacaciones.",
    "Solicitud de pruebas: se piden los testimonios de tres vecinos, el dictamen pericial del avalúo del inmueble y el interrogatorio de parte del demandado, que deberá absolver en la audiencia inicial.",
    "Respetado señor juez: yo le presto plata a mi vecino hace dos años y no me ha pagado, tengo una letra firmada. Quiero demandarlo para que me paguen el capital y los intereses, y que le embarguen lo que tenga.",
    "Pretensión subsidiaria: en caso de que no se acceda a la resolución del contrato, se solicita su cumplimiento forzado, con la entrega del bien y el pago de la cláusula penal pactada por las partes.",
    "Se interpone demanda de reparación directa contra la entidad estatal por la falla del servicio que causó la muerte del familiar de los demandantes. Se estima el daño moral en cien salarios mínimos legales.",
    "Acción reivindicatoria: el demandante es propietario del lote según escritura pública registrada, y el demandado lo ocupa sin título alguno. Se pide la restitución del predio y el pago de los frutos civiles.",
    "El demandado fue notificado del auto admisorio y no contestó la demanda dentro del término de traslado. Por lo tanto, se solicita dictar sentencia anticipada y acceder a las pretensiones.",
    "Fundamentos de derecho: artículos 1494 y 1546 del Código Civil. Anexos: poder para actuar, copia de la escritura, certificado de tradición y libertad, y constancia de la conciliación extrajudicial agotada.",
    "Demanda de impugnación de acta de asamblea de copropietarios: se pide declarar la nulidad de la decisión que aumentó las cuotas extraordinarias sin el quórum exigido por el reglamento de propiedad horizontal.",
    "En calidad de apoderado de la sociedad demandante, solicito que se libre mandamiento de pago por la suma de cuarenta millones de pesos más intereses, y que se decrete el embargo y secuestro de los bienes del demandado.",
    "Demando la declaración de unión marital de hecho entre compañeros permanentes y la existencia de la sociedad patrimonial, pues convivimos de manera singular y continua durante más de dos años.",
    "Pretendo que se condene al demandado a indemnizar los perjuicios materiales y morales ocasionados por el incumplimiento del contrato de obra, y que se le ordene pagar las costas y agencias en derecho.",
    "Demanda de pertenencia que incluye un derecho fundamental invocado de pasada: la parte actora dice que su vivienda digna está en riesgo, pero lo que se pide al juez es la declaración de dominio sobre el inmueble y su registro.",
    "Presentamos demanda de cobro por incumplimiento de las cuotas del crédito hipotecario; se solicita que se ordene el remate del inmueble gravado y que, con su producto, se pague la obligación al banco acreedor.",
]

FRONTERIZOS = {
    "Hice una solicitud a la entidad": "frontera: tutela que menciona una petición previa sin respuesta",
    "Demanda de pertenencia que incluye": "frontera: demanda que menciona un derecho fundamental de pasada",
}


def main():
    filas = []
    n = 0
    for categoria, textos in (("Tutela", TUTELA), ("Derecho de petición", PETICION), ("Demanda", DEMANDA)):
        for i, t in enumerate(textos):
            n += 1
            filas.append({
                "id": n, "texto": t, "categoria": categoria, "origen": "sintetizado",
                "revisado_por": revisor(i),
                "nota": next((v for k, v in FRONTERIZOS.items() if t.startswith(k)), ""),
            })
    destino = Path(__file__).parent / "dataset.csv"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "texto", "categoria", "origen", "revisado_por", "nota"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} fragmentos -> {destino}")


if __name__ == "__main__":
    main()
