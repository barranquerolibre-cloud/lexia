const $ = (selector) => document.querySelector(selector);
const input = $('#document');
const examples = {
  trabajo: 'Solicito la protección de mi derecho al trabajo y a la estabilidad laboral reforzada. Mi empleador terminó el contrato mientras me encontraba en tratamiento médico, sin autorización de la autoridad competente. Pido que se ordene mi reintegro al cargo y se restablezca mi afiliación a la seguridad social.',
  vital: 'Desde hace tres meses no recibo el pago de mi mesada pensional, que constituye mi único ingreso. No cuento con recursos para comprar alimentos, pagar el arriendo ni adquirir mis medicamentos. Solicito el amparo de mi mínimo vital y que se ordene reanudar el pago de las mesadas pendientes.',
  merito: 'Participé en un concurso de méritos y ocupé el primer lugar en la lista de elegibles para un cargo público. A pesar de existir una vacante definitiva y de estar vigente la lista, la entidad se ha negado a realizar el nombramiento. Solicito la protección de mis derechos de acceso a cargos públicos y debido proceso.'
};
const categories = {
  trabajo: {name: 'Derecho al trabajo', description: 'Asuntos relacionados con la protección del vínculo laboral, la estabilidad y el reintegro.'},
  vital: {name: 'Mínimo vital', description: 'Asuntos relacionados con los recursos indispensables para la subsistencia y una vida digna.'},
  merito: {name: 'Meritocracia', description: 'Asuntos relacionados con concursos públicos, listas de elegibles y acceso por mérito.'}
};
let selectedExample = null;
let pending = null;
function error(message = '') { $('#error').textContent = message; $('#error').hidden = !message; }
function updateCount() { $('#counter').textContent = `${input.value.length.toLocaleString('es-CO')} caracteres`; }
function showResult(state) {
  for (const name of ['empty', 'loading', 'filled']) $(`#${name}-result`).hidden = name !== state;
  $('.result-panel').setAttribute('aria-busy', String(state === 'loading'));
}
function cancel() { clearTimeout(pending); pending = null; $('#classify').disabled = false; $('#classify span').textContent = 'Analizar documento'; }
function invalidate() { cancel(); error(); showResult('empty'); }
function tab(name) {
  document.querySelectorAll('.tab').forEach(button => {
    const active = button.dataset.tab === name;
    button.classList.toggle('active', active);
    button.setAttribute('aria-selected', String(active));
    button.tabIndex = active ? 0 : -1;
  });
  $('#write-pane').hidden = name !== 'write'; $('#upload-pane').hidden = name !== 'upload';
}
input.addEventListener('input', () => { selectedExample = null; updateCount(); invalidate(); });
document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => tab(button.dataset.tab)));
document.querySelectorAll('.tab').forEach(button => button.addEventListener('keydown', event => {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  event.preventDefault();
  const next = event.key === 'Home' ? 'write' : event.key === 'End' ? 'upload' : button.dataset.tab === 'write' ? 'upload' : 'write';
  tab(next);
  document.querySelector(`[data-tab="${next}"]`).focus();
}));
document.querySelectorAll('[data-example]').forEach(button => button.addEventListener('click', () => {
  selectedExample = button.dataset.example; input.value = examples[selectedExample]; updateCount(); invalidate(); tab('write'); input.focus();
}));
function reset() {
  invalidate(); input.value = ''; selectedExample = null; $('#file').value = ''; $('#file-name').textContent = ''; updateCount(); tab('write'); input.focus();
}
$('#clear').addEventListener('click', reset);
$('#again').addEventListener('click', reset);
async function loadFile(file) {
  if (!file) return;
  invalidate();
  if (!file.name.toLowerCase().endsWith('.txt')) return error('Selecciona un archivo de texto con extensión .txt.');
  if (file.size > 1024 * 1024) return error('El archivo supera 1 MB. Selecciona un fragmento más pequeño.');
  try {
    const content = await file.text();
    if (!content.trim()) return error('El archivo está vacío. Selecciona otro documento.');
    if (content.length > 30000) return error('El texto supera 30.000 caracteres. Carga un fragmento más breve.');
    input.value = content; selectedExample = null; updateCount(); $('#file-name').textContent = `✓ ${file.name} · cargado correctamente`; tab('write');
  } catch { error('No se pudo leer el archivo. Intenta seleccionarlo nuevamente.'); }
}
$('#file').addEventListener('change', event => loadFile(event.target.files[0]));
const dropzone = $('#dropzone');
for (const name of ['dragenter', 'dragover']) dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.add('dragging'); });
for (const name of ['dragleave', 'drop']) dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.remove('dragging'); });
dropzone.addEventListener('drop', event => loadFile(event.dataTransfer.files[0]));
dropzone.tabIndex = 0;
dropzone.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); $('#file').click(); } });
$('#classify').addEventListener('click', () => {
  error();
  if (input.value.trim().length < 40) { error('Ingresa al menos 40 caracteres para explorar el flujo de análisis.'); input.focus(); return; }
  cancel(); showResult('loading'); $('#classify').disabled = true; $('#classify span').textContent = 'Preparando demostración…';
  // Mockup: fixed example data, deliberately independent of the entered text.
  // Replace this block with the backend response in the integration stage.
  const key = selectedExample || 'merito';
  pending = setTimeout(() => {
    $('#category-name').textContent = categories[key].name;
    $('#category-description').textContent = categories[key].description;
    const order = [key, ...Object.keys(categories).filter(other => other !== key)];
    $('#bars').replaceChildren();
    order.forEach((category, index) => {
      const value = [76, 16, 8][index];
      const row = document.createElement('div'); row.className = 'bar-row';
      const label = document.createElement('div'); label.className = 'bar-label';
      const name = document.createElement('span'); name.textContent = categories[category].name;
      const percent = document.createElement('span'); percent.textContent = `${value}%`;
      label.append(name, percent);
      const track = document.createElement('div'); track.className = 'bar-track';
      const fill = document.createElement('div'); fill.className = 'bar-fill'; fill.style.width = `${value}%`;
      track.append(fill); row.append(label, track); $('#bars').append(row);
    });
    cancel(); showResult('filled');
    if (window.matchMedia('(max-width: 620px)').matches) $('.result-panel').scrollIntoView({behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
  }, 1000);
});
