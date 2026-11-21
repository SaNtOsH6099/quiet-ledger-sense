const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

// Chrome comes from CHROME_PATH when set (the GitHub Actions workflow
// sets it from the setup-chrome step); otherwise the local VM path.
const CHROME = process.env.CHROME_PATH || '/home/hatch/workspace/chrome-test/browsers/chrome/linux-155.0.8059.84/chrome-linux64/chrome';
const DIR = process.argv[2];

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
           '--allow-file-access-from-files',
           '--force-device-scale-factor=1',
           '--user-data-dir=' + path.join(DIR, '.profile-shot')],
  });
  for (const file of files) {
    const out = file.replace(/\.html$/, '.png');
    const page = await browser.newPage();
    await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 1 });
    await page.goto('file://' + path.join(DIR, file), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await new Promise(r => setTimeout(r, 300));
    await page.screenshot({ path: path.join(DIR, out) });
    console.log('shot:', out);
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
