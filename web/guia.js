// Página "Guía": recuadros en vivo que consultan el backend real.
function sinConexion(el, e) { el.replaceChildren(h('span', {class: 'pill est-revision-humana'}, 'Sin conexión'), ' ', e.message); }

function pintarModelo(el, datos) {
  const ms = datos.modelos || {};
  if (!Object.keys(ms).length) { el.textContent = 'Todavía no hay modelos entrenados. Ejecuta: python backend/entrenar.py'; return; }
  el.replaceChildren(
    h('table', {class: 'mini'},
      h('thead', {}, h('tr', {}, ['Modelo', 'Textos', 'Exactitud en prueba', 'Validación cruzada'].map(t => h('th', {}, t)))),
      h('tbody', {}, Object.values(ms).map(m => h('tr', {}, h('td', {}, `${m.titulo} (${m.origen_laboratorio})`), h('td', {}, String(m.muestras)),
        h('td', {}, `${pct(m.exactitud_prueba)} (n=${m.muestras_prueba})`), h('td', {}, `${pct(m.exactitud_cv_media)} ± ${pct(m.exactitud_cv_desv)}`))))),
    h('div', {class: 'alert warn'}, 'Las exactitudes de prueba usan pocos documentos; la validación cruzada es la cifra más fiable. Con datos sintéticos no demuestran desempeño en documentos reales.'));
}

async function salud() {
  const el = $('#live-salud'), modelo = $('#live-modelo');
  try {
    const {estado, ok, datos} = await api('/api/salud');
    el.replaceChildren(h('span', {class: 'pill ' + (ok ? 'est-atendido' : 'est-revision-humana')}, `GET /api/salud → HTTP ${estado}`), ' ', datos.mensaje);
    pintarModelo(modelo, datos);
  } catch (e) { sinConexion(el, e); sinConexion(modelo, e); }
}

async function pruebas() {
  const el = $('#live-pruebas');
  try {
    const {datos} = await api('/api/pruebas');
    if (!datos.disponible) { el.textContent = 'Aún no has ejecutado las pruebas. Corre: python pruebas/pruebas.py'; return; }
    el.replaceChildren(
      h('div', {}, h('strong', {}, `${datos.pasan}/${datos.total} casos pasan`), ` · ejecutado ${datos.fecha}`),
      h('table', {class: 'mini'}, h('thead', {}, h('tr', {}, ['#', 'Caso', 'Esperado', 'Obtenido', 'Estado'].map(t => h('th', {}, t)))),
        h('tbody', {}, datos.filas.map(f => h('tr', {}, h('td', {}, String(f.id)), h('td', {}, f.caso), h('td', {}, f.esperado), h('td', {}, f.obtenido),
          h('td', {class: f.estado === 'PASA' ? 'pass' : 'fail'}, f.estado))))));
  } catch (e) { sinConexion(el, e); }
}

async function registro() {
  const el = $('#log');
  try {
    const {datos} = await api('/api/registro?n=25');
    el.textContent = datos.lineas.length ? datos.lineas.join('\n') : 'Aún no hay peticiones registradas.';
    el.scrollTop = el.scrollHeight;
  } catch (e) { el.textContent = e.message; }
}

// Lista de entregables: se recuerda en este navegador (si el almacenamiento no está disponible, igual funciona).
function guardados() { try { return JSON.parse(localStorage.getItem('lexia-entregables') || '{}'); } catch { return {}; } }
document.querySelectorAll('#entregables input').forEach(c => {
  c.checked = !!guardados()[c.dataset.k];
  c.addEventListener('change', () => { try { localStorage.setItem('lexia-entregables', JSON.stringify({...guardados(), [c.dataset.k]: c.checked})); } catch { /* sin almacenamiento */ } });
});
$('#refrescar').addEventListener('click', registro);

iniciarPagina('guia');
salud(); pruebas(); registro();
