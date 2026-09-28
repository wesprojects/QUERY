// Interface fixes from the review of 2026-09-27: the "New panels" heights follow the trim (36"H is thin only, p16, p90) and the trim switch names the
// panels oval cannot keep; a page cite inside a tooltip stays text (slatwall brace, p133); back painted glass takes a p727 color and the magnetic
// backer (p500-501); the drawn top cap screen has its own right-click menu (p70-73); the 6" stacker is not offered on oval (p441-p444); the guide
// dialog names the June 2022 PDFs; the price note says the July 18, 2022 9% is applied (p1).
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1400, height: 900 } }); pg.on('dialog', d => d.accept());
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); let fails = 0; const ck = (n, ok, info) => { console.log((ok ? 'PASS ' : 'FAIL ') + n + (!ok && info ? ' — ' + info : '')); if (!ok) fails++; };
  await pg.goto('file://' + process.cwd() + '/dist/index.html'); await pg.evaluate(() => localStorage.clear()); await pg.reload(); await pg.waitForTimeout(400);
  const hs = () => pg.$$eval('#optHeight button', bs => bs.map(x => +x.dataset.h));
  ck('thin job: the New panels heights include 36"H (p16)', (await hs()).includes(36), JSON.stringify(await hs()));
  // one 48" panel, selected
  await pg.click('[data-tool="draw"]'); const box = await pg.locator('#plan').boundingBox(); await pg.mouse.move(box.x + 300, box.y + 250); await pg.mouse.down(); await pg.mouse.move(box.x + 520, box.y + 250, { steps: 8 }); await pg.mouse.up(); await pg.waitForTimeout(250);
  const pid = await pg.evaluate(() => Object.keys(window.answerDebug.P().panels)[0]);
  await pg.click('[data-tool="select"]').catch(() => {});
  const at = await pg.evaluate((id) => { const P = window.answerDebug.P(), p = P.panels[id], a = P.nodes[p.a], c = P.nodes[p.b], v = window.answerDebug.view; return v.toScreen ? v.toScreen((a.x + c.x) / 2, (a.y + c.y) / 2) : null; }, pid);
  if (at) await pg.mouse.click(box.x + at[0], box.y + at[1]); else await pg.mouse.click(box.x + 410, box.y + 250);
  await pg.waitForTimeout(250);
  // top cap screen: right-click the drawn screen
  await pg.selectOption('#pTcs', 'universal:13.5'); await pg.waitForTimeout(250);
  const sc = await pg.evaluate(() => (window.answerDebug.elevHits() || []).find(h => h.kind === 'topcapscreen'));
  await pg.locator('#elev').scrollIntoViewIfNeeded(); await pg.waitForTimeout(150); const eb = await pg.locator('#elev').boundingBox();
  if (sc) { await pg.mouse.click(eb.x + sc.x + sc.w / 2, eb.y + sc.y + sc.h / 2, { button: 'right' }); await pg.waitForTimeout(200); }
  const menu = await pg.evaluate(() => { const m = document.querySelector('.ctxmenu'); return m ? m.textContent : ''; });
  ck('right-clicking the drawn top cap screen opens its menu (p70-73)', /top cap screen/.test(menu) && /Remove top cap screen/.test(menu) && /Sarto, 19 1\/2/.test(menu), JSON.stringify({ menu: menu.slice(0, 160), sc, eb }));
  await pg.keyboard.press('Escape');
  // slatwall tooltip: the page cite stays text inside the title
  const tileSel = 'select[data-f="type"]';
  await pg.selectOption(`${tileSel} >> nth=0`, 'slatwall'); await pg.waitForTimeout(250);
  const brace = await pg.evaluate(() => { const s = document.querySelector('select[data-f="brace"]'); return s ? { title: s.getAttribute('title'), href: s.hasAttribute('href') } : null; });
  ck('the slatwall brace tooltip reads as text, with its page (p133), and gains no link attributes', !!brace && /monitor arm \(p133\)/.test(brace.title) && !brace.href && !/<a/.test(brace.title), JSON.stringify(brace));
  // back painted glass: color from p727 and the magnetic backer option
  await pg.selectOption(`${tileSel} >> nth=0`, 'back painted glass'); await pg.waitForTimeout(250);
  const colors = await pg.$$eval('select[data-f="glassColor"] option', os => os.map(o => o.value).filter(Boolean));
  ck('a back painted glass tile offers the 20 glass colors of p727', colors.length === 20 && colors.includes('6521 Truffle') && colors.includes('6BB4 Electric Indigo'), JSON.stringify(colors.slice(0, 4)));
  await pg.selectOption('select[data-f="glassColor"] >> nth=0', '6521 Truffle'); await pg.waitForTimeout(250);
  await pg.selectOption('select[data-f="magneticBacker"] >> nth=0', '1'); await pg.waitForTimeout(250);
  const seg = await pg.evaluate((id) => { const p = window.answerDebug.P().panels[id]; return p.sides.flat().find(x => x.type === 'back painted glass'); }, pid);
  ck('the chosen glass color and magnetic backer are kept on the tile (p500-501)', !!seg && seg.glassColor === '6521 Truffle' && seg.magneticBacker === true, JSON.stringify(seg));
  // 6" stacker offered on thin; switch to oval: heights and stackers follow the trim, and the switch names what oval cannot keep
  const thinStacks = await pg.$$eval('#pStack button', bs => bs.map(x => x.dataset.st || ''));
  ck('thin trim offers the 6" stacker (p34)', thinStacks.includes('6'), JSON.stringify(thinStacks));
  await pg.click('#pH button[data-h="36"]'); await pg.waitForTimeout(200);
  await pg.click('#trimSwitch button[data-trim="oval"]'); await pg.waitForTimeout(400);
  const toast = await pg.textContent('#toast');
  ck('switching to oval names the 36"H panel as a thin-trim height (p16, p90)', /36"H is a thin-trim height/.test(toast), toast);
  ck('oval job: the New panels heights leave out 36"H (p90)', !(await hs()).includes(36) && (await hs()).includes(42), JSON.stringify(await hs()));
  await pg.evaluate((id) => { const P = window.answerDebug.P(); P.panels[id].height = 42; window.answerDebug.refresh(); }, pid); await pg.waitForTimeout(250);
  const ovalStacks = await pg.$$eval('#pStack button', bs => bs.map(x => x.dataset.st || ''));
  ck('oval trim does not offer the 6" stacker (p441-p444)', ovalStacks.length > 1 && !ovalStacks.includes('6'), JSON.stringify(ovalStacks));
  await pg.click('#trimSwitch button[data-trim="thin"]'); await pg.waitForTimeout(400);
  ck('back to thin: 36"H is offered again', (await hs()).includes(36), JSON.stringify(await hs()));
  // guide dialog and price note
  const guideText = await pg.evaluate(() => document.getElementById('guide').textContent);
  ck('the guide dialog names the June 2022 PDFs (answer-2022-1.pdf pages 1-189, answer-2022-2.pdf 190-766)', /answer-2022-1\.pdf/.test(guideText) && /190–766/.test(guideText), guideText.slice(-260));
  await pg.click('[data-stage="spec"]'); await pg.waitForTimeout(400);
  const spec = await pg.textContent('#specBody');
  ck('the specification total says the prices are the June 2022 list + 9% from July 18, 2022 (p1)', /June 2022 list \+ 9% from July 18, 2022/.test(spec), spec.slice(-300));
  await pg.click('#bFinishes'); await pg.waitForTimeout(300); const fin = await pg.textContent('#finishBody');
  ck('Finishes & settings explains the 9% adjustment (p1)', /9% adjustment effective July 18, 2022 applied/.test(fin), fin.slice(-300));
  console.log(errs.length ? errs.join('\n') : 'no page errors'); if (errs.length) fails++;
  console.log(fails ? fails + ' FAILURES' : 'ALL PASS'); if (fails) process.exitCode = 1; await b.close(); })();
