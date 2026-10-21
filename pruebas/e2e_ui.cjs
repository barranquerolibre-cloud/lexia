// Prueba de interfaz con navegador real (Edge) contra el backend en http://127.0.0.1:5000
// Uso: node pruebas/e2e_ui.cjs   (usa playwright instalado en web/.preview/node_modules)
const { chromium } = require('../web/.preview/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const PUERTO = 5057;
const BASE = `http://127.0.0.1:${PUERTO}`;
const EVID = path.resolve(__dirname, '../evidencia');
for (const f of ['gestor_e2e.db', 'registro_e2e.log']) fs.rmSync(path.join(EVID, f), { force: true });
// Servidor propio con base de datos y registro aparte: no mezcla con los expedientes reales.
const servidor = spawn('python', [path.resolve(__dirname, '../backend/app.py')], { stdio: 'ignore',
  env: { ...process.env, GESTOR_PUERTO: String(PUERTO), GESTOR_DB: path.join(EVID, 'gestor_e2e.db'), GESTOR_LOG: path.join(EVID, 'registro_e2e.log'), PYTHONIOENCODING: 'utf-8' } });
const CAP = path.resolve(__dirname, '../evidencia/capturas');
const TXT = path.resolve(__dirname, 'textos');
fs.mkdirSync(CAP, { recursive: true });
(async () => {
  for (let i = 0; i < 60; i++) { try { await fetch(BASE + '/api/categorias'); break; } catch { await new Promise(r => setTimeout(r, 500)); } }
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errores = [];
  page.on('pageerror', e => errores.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|net::ERR/.test(m.text())) errores.push('console: ' + m.text()); });
  const shot = (n, full = true) => page.screenshot({ path: path.join(CAP, n + '.png'), fullPage: full });
  const ok = (c, m) => { if (!c) throw new Error('FALLO: ' + m); console.log('OK  ', m); };

  await page.goto(BASE + '/');
  await page.locator('#backend-badge.ok').waitFor();
  ok(true, 'Insignia «Modelo conectado» visible');
  await shot('01_radicar_inicio');

  await page.locator('#classify').click();
  await page.locator('#error').waitFor({ state: 'visible' });
  ok((await page.locator('#error').textContent()).includes('vacío'), 'Validación de texto vacío');
  await shot('02_validacion_texto_vacio');

  await page.locator('.category-card[data-example="tutela"]').click();
  await page.locator('#classify').click();
  await page.locator('#filled-result').waitFor({ state: 'visible' });
  ok((await page.locator('.res-cat').first().textContent()) === 'Tutela', 'Ejemplo de tutela → categoría real «Tutela»');
  ok(await page.locator('.bar-line').count() === 9, 'Nueve barras reales: tipo, rama (Lab 1) y asunto (Lab 2)');
  ok((await page.locator('.modelo-bloque').allTextContents()).join(' ').includes('Derecho al trabajo'), 'La tutela de trabajo recibe el asunto «Derecho al trabajo»');
  await shot('03_resultado_texto');

  await page.locator('#clear').click();
  await page.locator('[data-tab="upload"]').click();
  await page.locator('#file').setInputFiles([path.join(TXT, 'tutela_trabajo.pdf'), path.join(TXT, 'peticion_certificado.docx'), path.join(TXT, 'escaneo_sin_texto.pdf')]);
  ok(await page.locator('#file-list li').count() === 3, 'Se listan 3 archivos seleccionados');
  await page.locator('#classify').click();
  await page.locator('#filled-result').waitFor({ state: 'visible' });
  const cats = await page.locator('.res-card:not(.fail) .res-cat').allTextContents();
  ok(cats.join('|') === 'Tutela|Derecho de petición', 'PDF → Tutela, Word → Derecho de petición (' + cats.join(', ') + ')');
  ok(await page.locator('.res-card.fail').count() === 1, 'El PDF escaneado se reporta como error sin romper el lote');
  await shot('04_resultado_archivos_pdf_word');

  await page.goto(BASE + '/bandeja');
  await page.locator('tr.fila').first().waitFor();
  const filas = await page.locator('tr.fila').count();
  ok(filas === 3, `Bandeja con ${filas} expedientes: solo los radicados en esta prueba, sin datos de ejemplo`);
  await page.locator('#f-cat').selectOption('Demanda');
  await page.waitForTimeout(600);
  ok((await page.locator('tr.fila .cat-demanda').count()) === (await page.locator('tr.fila').count()), 'Filtro por categoría');
  await shot('05_bandeja_filtrada');
  await page.locator('#limpiar').click();
  await page.waitForTimeout(600);
  await shot('06_bandeja');

  await page.locator('tr.fila').first().click();
  await page.locator('#contenido').waitFor({ state: 'visible' });
  const modelo = await page.locator('#clasificacion .pill').first().textContent();
  await page.locator('#categoria').selectOption(modelo === 'Demanda' ? 'Tutela' : 'Demanda');
  await page.locator('#estado').selectOption('En revisión');
  await page.locator('#nota').fill('Revisado por el equipo: corrección de prueba.');
  await page.locator('#guardar').click();
  await page.locator('#msg.err').waitFor();
  ok((await page.locator('#msg').textContent()).includes('al menos una persona'), 'Guardar sin elegir revisor muestra un mensaje claro');
  await page.locator('#lista-revisores input[value="Willigton Herrera"]').check();
  await page.locator('#lista-revisores input[value="Leidy Laura Blandon"]').check();
  await page.locator('#guardar').click();
  await page.locator('#msg.ok').waitFor();
  ok((await page.locator('#clasificacion').innerText()).includes('Revisado por: Willigton Herrera, Leidy Laura Blandon'), 'El expediente muestra «Revisado por» con los nombres');
  const ficha = await page.request.get(BASE + await page.locator('#ficha').getAttribute('href'));
  ok(ficha.status() === 200 && (await ficha.body()).subarray(0, 4).toString() === '%PDF', 'La ficha PDF del expediente se descarga');
  ok((await page.locator('#historial li').allTextContents()).some(t => t.includes('corregid')), 'Corrección humana guardada en el historial');
  ok(!(await page.locator('main').innerText()).includes('null'), 'El expediente no muestra valores «null»');
  await shot('07_expediente_corregido');
  await page.goto(BASE + '/bandeja');
  await page.locator('tr.fila').first().waitFor();
  ok((await page.locator('tbody').innerText()).includes('Willigton Herrera'), 'La bandeja muestra quién revisó cada expediente');
  await shot('07b_bandeja_con_revisor');

  await page.goto(BASE + '/guia');
  await page.locator('#live-pruebas table').waitFor();
  await page.waitForFunction(() => /GET \/api\/registro|GET \/api\/salud/.test(document.querySelector('#log').textContent));
  await shot('08_guia');

  // Responsive
  await page.setViewportSize({ width: 390, height: 900 });
  for (const ruta of ['/', '/bandeja', '/guia']) {
    await page.goto(BASE + ruta);
    await page.waitForTimeout(500);
    const desborda = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    ok(!desborda, `Sin desborde horizontal en móvil (390 px) en ${ruta}`);
  }
  await shot('09_movil_guia');
  await page.goto(BASE + '/');
  await shot('10_movil_radicar');

  // Backend caído: se simula cortando la red hacia /api
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.route('**/api/**', r => r.abort());
  await page.goto(BASE + '/');
  await page.locator('#backend-badge.fail').waitFor();
  await page.locator('.category-card[data-example="demanda"]').click();
  await page.locator('#classify').click();
  await page.locator('#error').waitFor({ state: 'visible' });
  ok((await page.locator('#error').textContent()).includes('No hay conexión con el backend'), 'Mensaje claro con el backend caído');
  await shot('11_backend_caido');

  ok(errores.length === 0, 'Sin errores de JavaScript' + (errores.length ? ': ' + errores.join(' | ') : ''));
  await browser.close();
  servidor.kill();
  console.log('\nPASS: prueba de interfaz completa. Capturas en evidencia/capturas');
})().catch(e => { console.error(e.message); servidor.kill(); process.exit(1); });
