// Prueft Ueberlauf, Ankerziele, Klickgroessen und Konsolenfehler.
// Schreibt Screenshots nach shots/.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FILE = 'file://' + path.resolve(__dirname, 'defendpro_homepage.html');
const SHOTS = path.resolve(__dirname, 'shots');
const WIDTHS = [390, 834, 1180, 1440, 1600];

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  let bad = 0;

  for (const w of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();

    const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));

    await page.goto(FILE, { waitUntil: 'load' });
    await page.waitForTimeout(250);

    const r = await page.evaluate(() => {
      const de = document.documentElement;

      // Ein Element ragt nur dann wirklich heraus, wenn kein Vorfahre es
      // beschneidet. Sonst meldet der Test Wasserzeichen und ausgelagerte
      // Skip-Links, die den Viewport nie verbreitern.
      const clipped = (el) => {
        for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
          const o = getComputedStyle(p).overflowX;
          if (o === 'hidden' || o === 'clip' || o === 'auto' || o === 'scroll') return true;
        }
        return false;
      };

      const over = [];
      for (const el of document.querySelectorAll('body *')) {
        const b = el.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) continue;
        if (b.right <= de.clientWidth + 1.5) continue;   // nur Ueberlauf nach rechts zaehlt in LTR
        if (clipped(el)) continue;
        over.push(`${el.tagName.toLowerCase()}.${(el.className || '').toString().split(' ')[0]} r=${b.right.toFixed(0)} l=${b.left.toFixed(0)}`);
      }
      // Klickziele
      const small = [];
      for (const el of document.querySelectorAll('a[href], button, summary, input, select, textarea')) {
        const b = el.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) continue;
        if (b.height < 24 || b.width < 24) small.push(`${el.tagName.toLowerCase()} "${(el.textContent || '').trim().slice(0, 28)}" ${b.width.toFixed(0)}x${b.height.toFixed(0)}`);
      }
      return {
        scrollW: de.scrollWidth,
        clientW: de.clientWidth,
        docH: document.body.scrollHeight,
        over: over.slice(0, 8),
        small: small.slice(0, 8),
        navH: (document.querySelector('.nav') || {}).offsetHeight,
      };
    });

    const overflow = r.scrollW > r.clientW + 1;
    const flag = (overflow || r.over.length || r.small.length || errors.length) ? 'FEHLER' : 'ok';
    if (flag === 'FEHLER') bad++;

    console.log(`\n${w}px  ${flag}`);
    console.log(`  scrollWidth ${r.scrollW} / clientWidth ${r.clientW}   Hoehe ${r.docH}px   Nav ${r.navH}px`);
    if (r.over.length) console.log('  Ueberlauf:', r.over);
    if (r.small.length) console.log('  Klickziel < 24px:', r.small);
    if (errors.length) console.log('  Konsole:', errors);

    await page.screenshot({ path: path.join(SHOTS, `w${w}.png`), fullPage: true });
    await ctx.close();
  }

  // Ankerpruefung im Browser
  const ctx = await browser.newContext({ viewport: { width: 1180, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(FILE, { waitUntil: 'load' });
  const anchors = await page.evaluate(() => {
    const dead = [];
    for (const a of document.querySelectorAll('a[href^="#"]')) {
      const id = a.getAttribute('href').slice(1);
      if (id && !document.getElementById(id)) dead.push(id);
    }
    const sm = getComputedStyle(document.querySelector('section')).scrollMarginTop;
    return { dead, scrollMarginTop: sm };
  });
  console.log(`\nTote Anker: ${anchors.dead.length ? anchors.dead.join(', ') : 'keine'}`);
  console.log(`scroll-margin-top: ${anchors.scrollMarginTop}`);
  if (anchors.dead.length) bad++;
  await ctx.close();

  await browser.close();
  console.log(bad ? `\nErgebnis: ${bad} Breite(n) mit Befund` : '\nErgebnis: bestanden');
  process.exit(bad ? 1 : 0);
})();
