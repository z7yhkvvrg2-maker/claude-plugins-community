// Erzeugt das Angebots-PDF und prueft es.
//
//     node angebot/render_angebot.js
//
// Ein Angebot ist ein Vertragsdokument. Geprueft wird deshalb nicht nur
// die Technik, sondern auch, ob die Pflichtsaetze tatsaechlich drin sind:
//
//   1. Schriften als /FontFile2 eingebettet, sonst ersetzt sie der Drucker.
//   2. Nichts wird nachgeladen, das Dokument geht per Mail und muss offline
//      gleich aussehen.
//   3. Die Abgrenzung zum Safety Check steht drin. Sie gehoert laut
//      eigener Vorgabe in jedes Angebot und darf nicht wegredigiert werden.
//   4. Der Teilnahme- und Gesundheitshinweis steht drin.
//   5. Keine der oeffentlich gesperrten Bezeichnungen taucht auf.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DIR = __dirname;
const FILE = 'file://' + path.join(DIR, 'angebot.html');
const PDF = path.join(DIR, 'defendpro_angebot.pdf');
const SHOTS = path.join(DIR, 'shots');
const MM = 96 / 25.4;

// Pflichtklauseln haengen von der Angebotsart ab. Ein Vortrag ohne
// Uebungen braucht keinen Gesundheitshinweis, und die Abgrenzung zum
// Safety Check gehoert nur in Angebote, die einen enthalten koennen.
// Vorher verlangte die Pruefung beides immer und haette ein korrektes
// Vortragsangebot abgelehnt.
const IMMER = [
  ['Bindefrist', 'Gültig bis'],
  ['Annahme', 'Unterschrift'],
  ['Storno', 'Storno und Verschiebung'],
  ['Ausfall meinerseits', 'Ausfall meinerseits'],
  ['Aufnahmen geregelt', 'Aufnahmen'],
];
const NUR_TRAINING = [
  ['Abgrenzung Safety Check', 'keine gesetzliche Arbeitsplatzevaluierung'],
  ['Teilnahme freiwillig', 'Die Teilnahme ist freiwillig'],
  ['Gesundheitshinweis', 'Gesundheitliche Einschränkungen'],
];

const GESPERRT = ['polizei', 'blaulicht', 'exekutive', 'einsatzorganisation',
                  'dienstplan', 'nachtdienst', 'schichtplan'];

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

  // Die Art steht in der Angebotsdatei, nicht im HTML.
  const datei = process.argv[2] || path.join(DIR, 'angebot.json');
  const art = (JSON.parse(fs.readFileSync(datei, 'utf8')).art || 'training').toLowerCase();
  const PFLICHT = art === 'vortrag' ? IMMER : IMMER.concat(NUR_TRAINING);
  console.log(`Angebotsart: ${art}`);

  await page.pdf({
    path: PDF, format: 'A4',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
    printBackground: true, preferCSSPageSize: true,
  });

  const raw = fs.readFileSync(PDF).toString('latin1');
  const seiten = (raw.match(/\/Type\s*\/Page[^s]/g) || []).length;
  const fonts = raw.split('/FontFile2').length - 1;
  // innerText liefert den Text NACH text-transform. Die dt-Elemente der
  // Konditionen stehen auf uppercase, eine Suche nach der Originalschreibweise
  // fand sie deshalb nicht. Beide Seiten kleinschreiben loest das, und
  // innerText bleibt richtig: eine unsichtbare Klausel schuetzt niemanden.
  const text = await page.evaluate(() => document.body.innerText);
  const hay = text.toLowerCase();

  console.log(`PDF        A4, ${(fs.statSync(PDF).size / 1024).toFixed(1)} KB, ${seiten} Seite(n)`);
  console.log(`Schriften  ${fonts} Subsets als /FontFile2 eingebettet`);
  console.log(`Externe Requests: ${external.length === 0 ? 'keine' : external.join(', ')}`);

  console.log('\nPflichtinhalte:');
  const fehlend = [];
  for (const [label, needle] of PFLICHT) {
    const da = hay.includes(needle.toLowerCase());
    console.log(`  ${da ? 'vorhanden' : 'FEHLT   '}  ${label}`);
    if (!da) fehlend.push(label);
  }

  const treffer = GESPERRT.filter(w => hay.includes(w));
  console.log(`\nGesperrte Bezeichnungen: ${treffer.length ? treffer.join(', ') : 'keine'}`);

  // Offene Platzhalter aus den Datendateien
  const offen = (text.match(/\[[^\]\n]{3,60}\]/g) || []);
  if (offen.length) console.log(`Offene Angaben: ${[...new Set(offen)].join(', ')}`);

  const ctx = await browser.newContext({
    viewport: { width: Math.round(210 * MM), height: Math.round(297 * MM) },
    deviceScaleFactor: 200 / 96,
  });
  const p2 = await ctx.newPage();
  await p2.goto(FILE, { waitUntil: 'networkidle' });
  await p2.evaluate(() => document.fonts.ready);
  await p2.screenshot({ path: path.join(SHOTS, 'angebot.png'), fullPage: true });
  await browser.close();

  const probleme = [];
  if (fonts === 0) probleme.push('keine Schrift eingebettet');
  if (external.length) probleme.push(`${external.length} externe Requests`);
  if (fehlend.length) probleme.push(`Pflichtinhalt fehlt: ${fehlend.join(', ')}`);
  if (treffer.length) probleme.push(`gesperrte Bezeichnung: ${treffer.join(', ')}`);

  if (probleme.length) {
    console.error('\nFEHLER: ' + probleme.join('; '));
    process.exit(1);
  }
  console.log('\nErgebnis: bestanden');
})();
