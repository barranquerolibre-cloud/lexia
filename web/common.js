// Utilidades compartidas por todas las páginas del gestor.
const $ = (s, root = document) => root.querySelector(s);

/** Crea un elemento DOM de forma segura (texto siempre como textContent). */
function h(tag, attrs = {}, ...hijos) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v == null) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const c of hijos.flat()) if (c != null && c !== false) el.append(c.nodeType ? c : document.createTextNode(c));
  return el;
}

/** Llama al backend. Devuelve {estado, datos}; lanza Error con mensaje claro si no hay conexión. */
async function api(ruta, opciones) {
  let resp;
  try {
    resp = await fetch(ruta, opciones);
  } catch {
    const e = new Error('No hay conexión con el backend. Verifica que esté ejecutándose: python backend/app.py');
    e.sinConexion = true;
    throw e;
  }
  const datos = await resp.json().catch(() => null);
  if (!datos) throw new Error(`Respuesta inesperada del servidor (HTTP ${resp.status}).`);
  return {estado: resp.status, ok: resp.ok, datos};
}

const CAT_CLASE = {'Tutela': 'cat-tutela', 'Derecho de petición': 'cat-peticion', 'Demanda': 'cat-demanda'};
const EST_CLASE = {'Clasificado': 'est-clasificado', 'Requiere revisión': 'est-revision-humana', 'En revisión': 'est-en-revision', 'Atendido': 'est-atendido'};
const pillCat = c => h('span', {class: `pill ${CAT_CLASE[c] || ''}`}, c);
const pillEst = e => h('span', {class: `pill ${EST_CLASE[e] || ''}`}, e);
const pillRama = c => h('span', {class: 'pill rama'}, c);
const pillTema = c => h('span', {class: 'pill tema'}, c);
const pct = x => `${Math.round(x * 100)}%`;
const fecha = iso => new Date(iso + (iso.length === 10 ? 'T00:00:00' : '')).toLocaleDateString('es-CO', {day: 'numeric', month: 'short', year: 'numeric'});
const fechaHora = iso => new Date(iso).toLocaleString('es-CO', {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'});

function textoVence(d) {
  if (d.estado === 'Atendido') return h('span', {class: 'venc'}, 'Atendido');
  const n = d.dias_restantes;
  const msg = n < 0 ? `Vencido hace ${-n} d` : n === 0 ? 'Vence hoy' : `Vence en ${n} d`;
  return h('span', {class: 'venc' + (n < 0 ? ' late' : '')}, `${msg} · ${fecha(d.fecha_limite)}`);
}

/** Barras de probabilidad reales devueltas por el modelo. */
function barras(probs) {
  const orden = Object.entries(probs).sort((a, b) => b[1] - a[1]);
  return h('div', {class: 'bars', role: 'list'}, orden.map(([cat, p], i) =>
    h('div', {class: 'bar-line' + (i === 0 ? ' top' : ''), role: 'listitem'},
      h('span', {}, cat), h('div', {class: 'track'}, h('div', {class: 'fill', style: `width:${(p * 100).toFixed(1)}%`})), h('span', {}, pct(p)))));
}

/** Bloque de un modelo: propuesta, confianza, barras reales y corrección humana si la hubo.
 *  res = {modelo, categoria, confianza, probabilidades}; `modelo` es lo que propuso el clasificador. */
function bloqueModelo(titulo, lab, res, pill) {
  const manual = !res.modelo;
  const corregido = !manual && res.categoria !== res.modelo;
  return h('section', {class: 'modelo-bloque'},
    h('div', {class: 'bloque-top'}, h('strong', {}, titulo), h('span', {class: 'lab-tag'}, lab)),
    h('div', {class: 'res-meta'}, pill(manual ? res.categoria : res.modelo),
      h('span', {class: 'res-file'}, manual ? 'Asignado por una persona' : `Confianza del modelo: ${pct(res.confianza)}`)),
    corregido ? h('div', {class: 'alert ok'}, `Una persona corrigió esta categoría a «${res.categoria}».`) : null,
    manual ? null : barras(res.probabilidades));
}

function barraLateral(activa) {
  const item = (href, clave, icono, texto) => h('a', {class: 'nav' + (activa === clave ? ' active' : ''), href}, h('span', {}, icono), texto);
  return [
    h('a', {class: 'brand', href: '/'}, h('span', {class: 'brand-mark'}, 'L', h('span', {}, '·')), 'lexia', h('span', {class: 'brand-dot'}, '.')),
    h('div', {class: 'workspace-label'}, 'GESTOR JURÍDICO'),
    item('/', 'radicar', '＋', 'Radicar'),
    item('/bandeja', 'bandeja', '▦', 'Bandeja'),
    item('/guia', 'guia', '✓', 'Guía paso a paso'),
    h('div', {class: 'sidebar-card'}, h('span', {class: 'small-icon'}, '✧'),
      h('h3', {}, 'La tecnología apoya.', h('br'), 'Tu criterio decide.'),
      h('p', {}, 'El modelo propone una categoría; una persona la confirma o la corrige.')),
    h('div', {class: 'sidebar-footer'}, h('span', {class: 'avatar'}, 'IA'), h('div', {}, 'IA & Derecho', h('small', {}, 'Laboratorio 03')), h('span', {class: 'footer-dot'})),
  ];
}

/** Monta el menú lateral y la insignia de estado del backend. */
async function iniciarPagina(activa) {
  const lateral = $('.sidebar');
  if (lateral) lateral.replaceChildren(...barraLateral(activa));
  const insignia = $('#backend-badge');
  if (!insignia) return null;
  try {
    const {ok, datos} = await api('/api/salud');
    insignia.className = 'backend-badge ' + (ok ? 'ok' : 'fail');
    insignia.replaceChildren(h('i'), ok ? 'Modelo conectado' : 'Modelo no disponible');
    insignia.title = datos.mensaje;
    return datos;
  } catch (e) {
    insignia.className = 'backend-badge fail';
    insignia.replaceChildren(h('i'), 'Backend sin conexión');
    insignia.title = e.message;
    return null;
  }
}
