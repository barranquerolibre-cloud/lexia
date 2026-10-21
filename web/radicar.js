// Página "Radicar": envía texto o archivos al backend y muestra la respuesta real del modelo.
const entrada = $('#document');
const EJEMPLOS = {
  tutela: ['Despido durante tratamiento médico', 'Fui despedida sin justa causa mientras me encontraba en tratamiento médico, sin que el Ministerio del Trabajo autorizara mi desvinculación. Acudo a la acción de tutela para que se proteja mi derecho al trabajo y a la estabilidad laboral reforzada y se ordene mi reintegro al cargo que desempeñaba.'],
  vital: ['Mesada pensional suspendida', 'Desde hace cuatro meses no recibo la mesada de mi pensión, que es mi único ingreso. No tengo recursos para alimentarme ni para pagar el arriendo. Presento acción de tutela para que se proteja mi mínimo vital y se ordene reanudar el pago de las mesadas pendientes.'],
  merito: ['Concurso sin nombramiento', 'Ocupé el primer lugar en la lista de elegibles del concurso de méritos y la entidad no ha expedido mi nombramiento pese a existir una vacante definitiva. Interpongo acción de tutela para proteger mi derecho de acceso a cargos públicos por mérito y el debido proceso.'],
  peticion: ['Certificación de aportes', 'En ejercicio del derecho de petición solicito respetuosamente que se me expida una certificación de los aportes realizados a mi nombre durante el último año, indicando fechas y valores, y que se me envíe por correo electrónico dentro del término legal.'],
  demanda: ['Incumplimiento de contrato', 'Señor Juez Civil del Circuito: por intermedio de apoderado presento demanda declarativa contra la sociedad demandada para que se declare el incumplimiento del contrato de suministro y se le condene al pago de los perjuicios, estimados en cuarenta millones de pesos. Hechos: primero, las partes suscribieron el contrato; segundo, la demandada no entregó la mercancía.'],
  nulidad: ['Nulidad de resolución sancionatoria', 'Se presenta demanda de nulidad y restablecimiento del derecho contra la resolución con la que la Superintendencia impuso una multa a la empresa sin respetar el debido proceso. Se pide que se declare la nulidad del acto administrativo y se restablezca el derecho de la demandante.'],
};
let archivos = [];
let enCurso = false;

function mostrar(estado) {
  for (const n of ['empty', 'loading', 'filled']) $(`#${n}-result`).hidden = n !== estado;
  $('.result-panel').setAttribute('aria-busy', String(estado === 'loading'));
}
function error(msg = '') { const e = $('#error'); e.textContent = msg; e.hidden = !msg; }
function contador() { $('#counter').textContent = `${entrada.value.length.toLocaleString('es-CO')} caracteres`; }
function pestana(nombre) {
  document.querySelectorAll('.tab').forEach(b => {
    const activa = b.dataset.tab === nombre;
    b.classList.toggle('active', activa); b.setAttribute('aria-selected', String(activa)); b.tabIndex = activa ? 0 : -1;
  });
  $('#write-pane').hidden = nombre !== 'write'; $('#upload-pane').hidden = nombre !== 'upload';
}
function pintarArchivos() {
  $('#file-list').replaceChildren(...archivos.map((f, i) => h('li', {},
    h('span', {}, `${f.name} · ${(f.size / 1024).toFixed(0)} KB`),
    h('button', {type: 'button', 'aria-label': `Quitar ${f.name}`, onclick: () => { archivos.splice(i, 1); pintarArchivos(); }}, '×'))));
}
function agregarArchivos(lista) {
  error();
  for (const f of lista) {
    if (archivos.length >= 10) { error('Máximo 10 archivos por envío.'); break; }
    if (f.size > 10 * 1024 * 1024) { error(`«${f.name}» supera 10 MB.`); continue; }
    archivos.push(f);
  }
  pintarArchivos();
}
function limpiar() {
  entrada.value = ''; archivos = []; $('#file').value = ''; $('#asunto').value = '';
  pintarArchivos(); contador(); error(); mostrar('empty'); pestana('write'); entrada.focus();
}

function tarjeta(r) {
  if (!r.ok) {
    return h('div', {class: 'res-card fail'}, h('div', {class: 'res-top'}, h('strong', {}, 'No se pudo radicar'), h('span', {class: 'res-file'}, r.archivo)),
      h('div', {class: 'alert err'}, r.error));
  }
  const d = r.documento;
  return h('div', {class: 'res-card'},
    h('div', {class: 'res-top'}, pillCat(d.categoria), h('span', {class: 'res-file'}, `Expediente #${d.id}${d.archivo ? ' · ' + d.archivo : ''}`)),
    h('div', {class: 'res-cat'}, d.categoria),
    h('p', {class: 'res-desc'}, `Plazo de referencia: ${d.plazo}.`),
    bloqueModelo('Tipo de documento', 'Gestor', {modelo: d.categoria_modelo, categoria: d.categoria, confianza: d.confianza, probabilidades: d.probabilidades}, pillCat),
    bloqueModelo('Rama del derecho', 'Laboratorio 1', d.rama, pillRama),
    d.tema ? bloqueModelo('Asunto de la tutela', 'Laboratorio 2', d.tema, pillTema)
           : h('p', {class: 'res-file'}, 'El asunto de la tutela (Laboratorio 2) solo se calcula cuando el documento es una tutela.'),
    h('div', {class: 'res-meta'}, pillEst(d.estado), textoVence(d)),
    d.estado === 'Requiere revisión'
      ? h('div', {class: 'alert warn'}, 'La confianza es baja en al menos un modelo. Una persona debe revisar y confirmar las categorías antes de seguir.')
      : h('div', {class: 'alert ok'}, 'Radicado. Revisa la categoría en el expediente y confírmala o corrígela.'),
    h('div', {class: 'res-actions'}, h('a', {class: 'btn', href: `/documento?id=${d.id}`}, 'Abrir expediente ↗'), h('a', {class: 'btn-sec', href: '/bandeja'}, 'Ver bandeja')));
}

async function radicar() {
  if (enCurso) return;
  error();
  const enArchivos = !$('#upload-pane').hidden;
  const asunto = $('#asunto').value.trim();
  let opciones;
  if (enArchivos) {
    if (!archivos.length) return error('Selecciona al menos un archivo (PDF, Word, .odt, .rtf o .txt).');
    const fd = new FormData();
    archivos.forEach(f => fd.append('archivo', f));
    fd.append('asunto', asunto);
    opciones = {method: 'POST', body: fd};
  } else {
    const texto = entrada.value.trim();
    if (!texto) { entrada.focus(); return error('El texto está vacío. Pega el contenido del documento o sube un archivo.'); }
    if (texto.length < 40) { entrada.focus(); return error(`El texto es muy corto (${texto.length} caracteres). Escribe al menos 40.`); }
    opciones = {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({texto, asunto})};
  }
  enCurso = true; $('#classify').disabled = true;
  $('#loading-msg').textContent = enArchivos ? 'Extrayendo el texto de los archivos y clasificando…' : 'Clasificando el texto…';
  mostrar('loading');
  try {
    const {datos} = await api('/api/documentos', opciones);
    if (datos.error && !datos.resultados) { mostrar('empty'); return error(datos.error); }
    $('#result-list').replaceChildren(...datos.resultados.map(tarjeta));
    mostrar('filled');
    if (matchMedia('(max-width: 900px)').matches) $('.result-panel').scrollIntoView({behavior: 'smooth', block: 'start'});
  } catch (e) {
    mostrar('empty'); error(e.message);
  } finally {
    enCurso = false; $('#classify').disabled = false;
  }
}

entrada.addEventListener('input', () => { contador(); error(); });
document.querySelectorAll('.tab').forEach(b => {
  b.addEventListener('click', () => pestana(b.dataset.tab));
  b.addEventListener('keydown', ev => {
    if (!['ArrowLeft', 'ArrowRight'].includes(ev.key)) return;
    ev.preventDefault(); const sig = b.dataset.tab === 'write' ? 'upload' : 'write'; pestana(sig); $(`[data-tab="${sig}"]`).focus();
  });
});
document.querySelectorAll('[data-example]').forEach(b => b.addEventListener('click', () => {
  const [asunto, texto] = EJEMPLOS[b.dataset.example];
  $('#asunto').value = asunto; entrada.value = texto; contador(); error(); pestana('write'); entrada.focus();
}));
$('#clear').addEventListener('click', limpiar);
$('#classify').addEventListener('click', radicar);
$('#file').addEventListener('change', ev => { agregarArchivos([...ev.target.files]); ev.target.value = ''; });
const zona = $('#dropzone');
zona.tabIndex = 0;
for (const n of ['dragenter', 'dragover']) zona.addEventListener(n, ev => { ev.preventDefault(); zona.classList.add('dragging'); });
for (const n of ['dragleave', 'drop']) zona.addEventListener(n, ev => { ev.preventDefault(); zona.classList.remove('dragging'); });
zona.addEventListener('drop', ev => agregarArchivos([...ev.dataTransfer.files]));
zona.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); $('#file').click(); } });

iniciarPagina('radicar');
