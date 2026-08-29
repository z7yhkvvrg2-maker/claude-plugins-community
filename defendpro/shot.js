// Screenshots einzelner Abschnitte, damit die Gestaltung beurteilbar ist.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FILE = 'file://' + path.resolve(__dirname, 'defendpro_homepage.html');
const OUT = path.resolve(__dirname, 'shots');

const GROUPS = {
  a_hero:    ['#start', 'section.band', '#situation'],
  b_angebot: ['#leistungen', '#bereiche'],
  c_system:  ['#system', '#ablauf'],
  d_formate: ['#formate', '#fragen'],
  e_person:  ['#person', '#buch'],
  f_kontakt: ['#kontakt'],
  g_recht:   ['#rechtliches', 'footer'],
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

  for (const [w, tag] of [[1180, 'desktop'], [390, 'mobil']]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    await page.goto(FILE, { waitUntil: 'load' });
    await page.waitForTimeout(200);

    for (const [name, sels] of Object.entries(GROUPS)) {
      const box = await page.evaluate((sels) => {
        let top = Infinity, bottom = -Infinity;
        for (const s of sels) {
          const el = document.querySelector(s);
          if (!el) continue;
          const r = el.getBoundingClientRect();
          top = Math.min(top, r.top + scrollY);
          bottom = Math.max(bottom, r.bottom + scrollY);
        }
        return { top, height: bottom - top };
      }, sels);
      if (!isFinite(box.top)) { console.log('fehlt:', name); continue; }
      await page.screenshot({
        path: path.join(OUT, `${tag}_${name}.png`),
        fullPage: true,
        clip: { x: 0, y: box.top, width: w, height: Math.min(box.height, 4200) },
      });
    }
    await ctx.close();
    console.log(`${tag} fertig`);
  }
  await browser.close();
})();
