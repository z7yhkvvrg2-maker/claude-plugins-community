// Erzeugt das PDF des Einseiters und prueft es.
//
//     node onepager/render_onepager.js
//
// Geprueft wird dreierlei, weil jedes davon still schiefgehen kann:
//   1. genau eine Seite. Ein Umbruch waere hier ein Fehler, kein Layout.
//   2. Schriften als /FontFile2 eingebettet. Sonst ersetzt der Drucker sie.
//   3. nichts wird nachgeladen. Der Einseiter muss offline gleich aussehen.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DIR = __dirname;
const FILE = 'file://' + path.join(DIR, 'einseiter.html');
const PDF = path.join(DIR, 'defendpro_einseiter.pdf');
const SHOTS = path.join(DIR, 'shots');
const MM = 96 / 25.4;

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage();

  const external = [];
  page.on('request', r => {
    if (!/^(file:|data:|blob:|about:)/.test(r.url())) external.push(r.url().slice(0, 80));
  });

  await page.goto(FILE, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  await page.pdf({
    path: PDF,
    format: 'A4',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
    printBackground: true,
    preferCSSPageSize: true,
  });

  const pdf = fs.readFileSync(PDF);
  const raw = pdf.toString('latin1');
  const pages = (raw.match(/\/Type\s*\/Page[^s]/g) || []).length;
  const fonts = raw.split('/FontFile2').length - 1;

  console.log(`PDF        A4, ${(pdf.length / 1024).toFixed(1)} KB`);
  console.log(`Seiten     ${pages}`);
  console.log(`Schriften  ${fonts} Subsets als /FontFile2 eingebettet`);
  console.log(`Externe Requests: ${external.length === 0 ? 'keine' : external.join(', ')}`);

  // Kontrollbild in 200 dpi
  const ctx = await browser.newContext({
    viewport: { width: Math.round(210 * MM), height: Math.round(297 * MM) },
    deviceScaleFactor: 200 / 96,
  });
  const p2 = await ctx.newPage();
  await p2.goto(FILE, { waitUntil: 'networkidle' });
  await p2.evaluate(() => document.fonts.ready);
  const overflow = await p2.evaluate(() => ({
    hoehe: Math.round(document.body.scrollHeight / (96 / 25.4)),
    ueberlauf: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  }));
  await p2.screenshot({ path: path.join(SHOTS, 'einseiter.png') });
  console.log(`Inhaltshoehe ${overflow.hoehe} mm von 297 mm verfuegbar`);

  await browser.close();

  const problems = [];
  if (pages !== 1) problems.push(`${pages} Seiten statt einer`);
  if (fonts === 0) problems.push('keine Schrift eingebettet');
  if (external.length) problems.push(`${external.length} externe Requests`);
  if (overflow.hoehe > 297) problems.push(`Inhalt ${overflow.hoehe} mm hoch, laeuft ueber`);

  if (problems.length) {
    console.error('\nFEHLER: ' + problems.join('; '));
    process.exit(1);
  }
  console.log('\nErgebnis: bestanden');
})();
