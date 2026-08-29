// Erzeugt das Druck-PDF und Kontrollbilder.
//
//     node card/render_card.js
//
// PDF:      91 x 61 mm, also 85 x 55 mm Endformat plus 3 mm Beschnitt.
// Kontrolle: PNG je Seite in 600 dpi, zusaetzlich eine Fassung mit
//            eingezeichneter Schnittkante und Sicherheitsabstand.

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DIR = __dirname;
const FILE = 'file://' + path.join(DIR, 'karte.html');
const SHOTS = path.join(DIR, 'shots');

const MM = 96 / 25.4;              // CSS-Pixel je Millimeter
const PAGE = { w: 91, h: 61 };
const BLEED = 3;
const SAFE = 7;
const DPI = 600;

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

  // --- Druck-PDF -----------------------------------------------------
  {
    const page = await browser.newPage();
    await page.goto(FILE, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: path.join(DIR, 'defendpro_visitenkarte.pdf'),
      width: `${PAGE.w}mm`,
      height: `${PAGE.h}mm`,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      printBackground: true,
      preferCSSPageSize: true,
    });
    await page.close();
    const kb = fs.statSync(path.join(DIR, 'defendpro_visitenkarte.pdf')).size / 1024;
    console.log(`PDF        91 x 61 mm, 2 Seiten, ${kb.toFixed(1)} KB`);
  }

  // --- Kontrollbilder -------------------------------------------------
  const scale = DPI / 96;
  const ctx = await browser.newContext({
    viewport: { width: Math.round(PAGE.w * MM), height: Math.round(PAGE.h * MM) },
    deviceScaleFactor: scale,
  });
  const page = await ctx.newPage();
  await page.goto(FILE, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  const sides = ['front', 'back'];

  // Die Seiten stehen im Fluss uebereinander. Ein Locator-Screenshot
  // rundet die Elementkante auf Geraetepixel und zieht dabei einen
  // schmalen Streifen der Nachbarseite mit herein. Deshalb wird die
  // jeweils andere Seite ausgeblendet und ab Nullpunkt geschnitten.
  const shot = async (name, suffix) => {
    await page.addStyleTag({ content: `.side:not(.${name}){display:none}`, id: 'iso' });
    await page.screenshot({
      path: path.join(SHOTS, `${sides.indexOf(name) + 1}_${name}${suffix}.png`),
      clip: { x: 0, y: 0, width: Math.round(PAGE.w * MM), height: Math.round(PAGE.h * MM) },
    });
    await page.evaluate(() => document.querySelectorAll('style').forEach(
      s => { if (s.textContent.includes('.side:not(')) s.remove(); }));
  };

  for (const s of sides) await shot(s, '');
  console.log(`Kontrolle  je Seite ein PNG in ${DPI} dpi`);

  // Hilfslinien einblenden: Schnittkante und Sicherheitsabstand.
  await page.addStyleTag({
    content: `
      .side::before,.side::after{content:"";position:absolute;pointer-events:none;z-index:99}
      .side::before{inset:${BLEED}mm;outline:.2mm dashed #E5484D}
      .side::after{inset:${SAFE}mm;outline:.2mm dashed #2E9E5B}
    `,
  });
  for (const s of sides) await shot(s, '_marken');
  console.log('Hilfslinien rot = Schnittkante 85 x 55 mm, gruen = Sicherheitsabstand');

  // --- Masspruefung ---------------------------------------------------
  const check = await page.evaluate(({ MM, PAGE, SAFE }) => {
    const out = [];
    for (const side of document.querySelectorAll('.side')) {
      const r = side.getBoundingClientRect();
      out.push({
        klasse: side.className,
        breite: +(r.width / MM).toFixed(2),
        hoehe: +(r.height / MM).toFixed(2),
      });
    }
    // Liegt sichtbarer Inhalt innerhalb des Sicherheitsabstands?
    const verstoss = [];
    for (const el of document.querySelectorAll('.side > *')) {
      if (el.classList.contains('watermark')) continue;   // darf bewusst anschneiden
      const s = el.closest('.side').getBoundingClientRect();
      const r = el.getBoundingClientRect();
      const l = (r.left - s.left) / MM, t = (r.top - s.top) / MM;
      const rr = (s.right - r.right) / MM, b = (s.bottom - r.bottom) / MM;
      const min = Math.min(l, t, rr, b);
      if (min < SAFE - 0.15) {
        verstoss.push(`${el.className}: ${min.toFixed(2)}mm zum Seitenrand`);
      }
    }
    return { out, verstoss, pageW: PAGE.w };
  }, { MM, PAGE, SAFE });

  console.log('\nSeitenmasse:');
  for (const s of check.out) console.log(`  ${s.klasse.padEnd(12)} ${s.breite} x ${s.hoehe} mm`);
  if (check.verstoss.length) {
    console.log('\nInhalt zu nah am Rand:');
    for (const v of check.verstoss) console.log('  x ' + v);
  } else {
    console.log('\nAlle Inhalte innerhalb des Sicherheitsabstands von 7 mm ab Seitenrand.');
  }

  await browser.close();
  process.exit(check.verstoss.length ? 1 : 0);
})();
