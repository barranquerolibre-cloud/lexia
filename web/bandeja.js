// Página "Bandeja": lista real de expedientes desde GET /api/documentos.
const filtros = {q: $('#q'), categoria: $('#f-cat'), rama: $('#f-rama'), tema: $('#f-tema'), revisor: $('#f-rev'), estado: $('#f-est')};
let temporizador;

function estadisticas(r) {
  const c = (titulo, valor, clase = '') => h('div', {class: 'stat ' + clase}, h('small', {}, titulo), h('strong', {}, String(valor)));
  $('#stats').replaceChildren(
    c('Total en bandeja', r.total), c('Requieren revisión', r.requieren_revision, r.requieren_revision ? 'warn' : ''),
    c('Plazos vencidos', r.vencidos, r.vencidos ? 'warn' : ''), c('Atendidos', r.por_estado.Atendido || 0));
}

function fila(d) {
  const abrir = () => { location.href = `/documento?id=${d.id}`; };
  return h('tr', {class: 'fila', tabindex: 0, onclick: abrir, onkeydown: ev => { if (ev.key === 'Enter') abrir(); }},
    h('td', {}, String(d.id)),
    h('td', {}, h('span', {class: 'asunto'}, d.asunto || d.archivo || 'Sin asunto'),
      h('span', {class: 'extracto'}, d.extracto)),
    h('td', {}, pillCat(d.categoria), d.corregido ? h('div', {class: 'extracto'}, `Modelo: ${d.categoria_modelo}`) : null,
      h('div', {style: 'margin-top:6px;display:flex;gap:5px;flex-wrap:wrap'}, pillRama(d.rama.categoria), d.tema ? pillTema(d.tema.categoria) : null)),
    h('td', {}, pct(d.confianza)),
    h('td', {}, pillEst(d.estado)),
    h('td', {}, d.revisado_por.length ? d.revisado_por.join(', ') : h('span', {class: 'extracto'}, 'Pendiente')),
    h('td', {}, textoVence(d), h('div', {class: 'extracto'}, d.plazo)));
}

async function cargar() {
  const p = new URLSearchParams();
  for (const [k, el] of Object.entries(filtros)) if (el.value.trim()) p.set(k, el.value.trim());
  try {
    const {ok, datos} = await api('/api/documentos?' + p);
    if (!ok) throw new Error(datos.error || 'No se pudo cargar la bandeja.');
    $('#error').hidden = true;
    estadisticas(datos.resumen);
    $('#filas').replaceChildren(...datos.documentos.map(fila));
    const hayFiltros = Object.values(filtros).some(el => el.value.trim());
    $('#vacio').replaceChildren(...(datos.resumen.total === 0 && !hayFiltros
      ? ['Aún no hay documentos radicados. ', h('a', {href: '/'}, 'Radica el primero →')]
      : ['No hay documentos con esos filtros.']));
    $('#vacio').hidden = datos.documentos.length > 0;
  } catch (e) {
    $('#error').textContent = e.message; $('#error').hidden = false;
    $('#filas').replaceChildren(); $('#stats').replaceChildren();
  }
}

filtros.q.addEventListener('input', () => { clearTimeout(temporizador); temporizador = setTimeout(cargar, 250); });
filtros.categoria.addEventListener('change', cargar);
filtros.estado.addEventListener('change', cargar);
filtros.rama.addEventListener('change', cargar);
filtros.revisor.addEventListener('change', cargar);
filtros.tema.addEventListener('change', cargar);
$('#limpiar').addEventListener('click', () => { Object.values(filtros).forEach(el => { el.value = ''; }); cargar(); });

iniciarPagina('bandeja');
api('/api/categorias').then(({datos}) => {
  filtros.revisor.append(...datos.integrantes.map(n => h('option', {value: n}, n)));
}).catch(() => {});
cargar();
