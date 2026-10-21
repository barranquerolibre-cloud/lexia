// Página "Expediente": detalle, corrección de categoría y cambio de estado (PUT /api/documentos/<id>).
const id = new URLSearchParams(location.search).get('id');
let doc = null;

function mensaje(texto, tipo) {
  const m = $('#msg'); m.textContent = texto; m.className = 'alert ' + tipo; m.hidden = !texto;
}
function alternarTema() { $('#campo-tema').hidden = $('#categoria').value !== 'Tutela'; }
function pintar(d) {
  doc = d;
  $('#crumb').textContent = `Expediente #${d.id}`;
  document.title = `Expediente #${d.id} · Lexia`;
  $('#sub').textContent = `RADICADO ${fecha(d.fecha_radicacion).toUpperCase()}${d.archivo ? ' · ' + d.archivo.toUpperCase() : ''}`;
  $('#titulo').textContent = d.asunto || d.archivo || `Expediente #${d.id}`;
  $('#texto').textContent = d.texto;
  const aviso = d.estado === 'Requiere revisión'
    ? h('div', {class: 'alert warn'}, 'Confianza baja en al menos un modelo: confirma o corrige las categorías antes de continuar.') : null;
  $('#clasificacion').replaceChildren(...[
    aviso,
    h('div', {class: 'res-meta'}, pillEst(d.estado), textoVence(d)), h('p', {class: 'res-desc'}, `Plazo de referencia: ${d.plazo}.`),
    d.revisado_por.length
      ? h('div', {class: 'alert ok'}, h('strong', {}, 'Revisado por: '), d.revisado_por.join(', '))
      : h('div', {class: 'alert warn'}, 'Revisión humana pendiente: ninguna persona ha confirmado esta clasificación todavía.'),
    bloqueModelo('Tipo de documento', 'Gestor', {modelo: d.categoria_modelo, categoria: d.categoria, confianza: d.confianza, probabilidades: d.probabilidades}, pillCat),
    bloqueModelo('Rama del derecho', 'Laboratorio 1', d.rama, pillRama),
    d.tema ? bloqueModelo('Asunto de la tutela', 'Laboratorio 2', d.tema, pillTema) : null,
  ].filter(Boolean));
  $('#historial').replaceChildren(...d.eventos.map(e => h('li', {}, h('time', {}, fechaHora(e.fecha)), e.evento)));
  $('#categoria').value = d.categoria; $('#rama').value = d.rama.categoria; $('#tema').value = d.tema ? d.tema.categoria : '';
  $('#estado').value = d.estado; $('#nota').value = d.nota || ''; alternarTema();
  document.querySelectorAll('#lista-revisores input').forEach(c => { c.checked = d.revisado_por.includes(c.value); });
  $('#ficha').href = `/api/documentos/${d.id}/ficha.pdf`;
}

async function guardar() {
  mensaje('');
  const revisores = [...document.querySelectorAll('#lista-revisores input:checked')].map(c => c.value);
  if (!revisores.length) return mensaje('Selecciona al menos una persona que revisó el documento para poder guardar.', 'err');
  $('#guardar').disabled = true;
  try {
    const {ok, datos} = await api(`/api/documentos/${id}`, {method: 'PUT', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({categoria: $('#categoria').value, rama: $('#rama').value, estado: $('#estado').value, nota: $('#nota').value, revisado_por: revisores,
        ...($('#categoria').value === 'Tutela' && $('#tema').value ? {tema: $('#tema').value} : {})})});
    if (!ok) return mensaje(datos.error || 'No se pudo guardar.', 'err');
    pintar(datos); mensaje('Cambios guardados y registrados en el historial.', 'ok');
  } catch (e) { mensaje(e.message, 'err'); }
  finally { $('#guardar').disabled = false; }
}

async function iniciar() {
  iniciarPagina('bandeja');
  if (!id || !/^\d+$/.test(id)) { $('#error').textContent = 'Falta el número de expediente. Abre uno desde la bandeja.'; $('#error').hidden = false; return; }
  try {
    const [{ok, datos}, cats] = await Promise.all([api(`/api/documentos/${id}`), api('/api/categorias')]);
    if (!ok) { $('#error').textContent = datos.error || 'No se pudo cargar el expediente.'; $('#error').hidden = false; return; }
    $('#categoria').replaceChildren(...cats.datos.categorias.map(c => h('option', {value: c.nombre}, c.nombre)));
    $('#rama').replaceChildren(...cats.datos.ramas.map(r => h('option', {value: r}, r)));
    $('#tema').replaceChildren(h('option', {value: ''}, '— sin asunto —'), ...cats.datos.temas.map(t => h('option', {value: t}, t)));
    $('#lista-revisores').replaceChildren(...cats.datos.integrantes.map(n =>
      h('label', {class: 'check'}, h('input', {type: 'checkbox', value: n}), ' ' + n)));
    $('#estado').replaceChildren(...cats.datos.estados.map(e => h('option', {value: e}, e)));
    $('#contenido').hidden = false;
    pintar(datos);
  } catch (e) { $('#error').textContent = e.message; $('#error').hidden = false; }
}
$('#guardar').addEventListener('click', guardar);
$('#categoria').addEventListener('change', alternarTema);
iniciar();
