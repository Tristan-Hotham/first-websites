// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server PORT; set PORT).
// MapLibre comes from a local npm copy (the CDN is not reachable from the build container); fonts are blocked here.
// NOML=1 blocks MapLibre too, to check the fallback SVG map.
const { chromium } = require("playwright");
const ML = process.env.MAPLIBRE_DIST || "/tmp/ml/node_modules/maplibre-gl/dist";
const fs = require("fs");
(async () => {
  fs.mkdirSync("qa", { recursive: true });
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const errs = [];
  const sizes = process.env.ONLY ? [[process.env.ONLY, process.env.ONLY === "phone" ? 390 : 1280, 860]] : [["desktop", 1280, 900], ["phone", 390, 844]];
  const tag = process.env.NOML ? "noml_" : "";
  for (const [nm, vw, vh] of sizes) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/googleapis|gstatic/, r => r.abort());
    if (process.env.NOML) await p.route(/maplibre-gl/, r => r.abort());
    else {
      await p.route(/maplibre-gl@[\d.]+\/dist\/maplibre-gl\.js/, r => r.fulfill({ path: ML + "/maplibre-gl.js", contentType: "application/javascript" }));
      await p.route(/maplibre-gl@[\d.]+\/dist\/maplibre-gl\.css/, r => r.fulfill({ path: ML + "/maplibre-gl.css", contentType: "text/css" }));
    }
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + process.env.PORT + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(3500);
    await p.screenshot({ path: `qa/${tag}${nm}_top.png` });
    const idle = () => p.evaluate(() => new Promise(r => { if (typeof map === "undefined" || !map || !map.loaded) return r(); let done = false; const fin = () => { if (!done) { done = true; r(); } }; map.once("idle", fin); map.triggerRepaint(); setTimeout(fin, 20000); }));
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(500); if (/atlas|map/.test(sel)) await idle(); await p.locator(sel).screenshot({ path: `qa/${tag}${nm}_${f}.png` }); };
    await shot("#atlas", "map");
    for (const y of [1990, 1992, 1993, 1995]) {
      await p.evaluate(y => { const r = document.getElementById("yr"); r.value = y; r.dispatchEvent(new Event("input")); }, y);
      await p.waitForTimeout(700); await shot("#atlas", "map_" + y);
    }
    await p.click("#play"); await p.waitForTimeout(2500); await p.click("#play");
    await p.click('#colRow [data-c="tld"]'); await p.evaluate(() => { const r = document.getElementById("yr"); r.value = 1994; r.dispatchEvent(new Event("input")); }); await p.waitForTimeout(800); await shot("#atlas", "map_tld_1994");
    await p.click('#colRow [data-c="web"]');
    await p.fill("#q", "Trojan"); await p.waitForTimeout(400); await p.keyboard.press("Enter"); await p.waitForTimeout(3000); await shot("#atlas", "search_coffee");
    await p.fill("#q", "Japan"); await p.waitForTimeout(400); await p.keyboard.press("Enter"); await p.waitForTimeout(3000); await shot("#atlas", "country_japan");
    await p.click(".back"); await p.waitForTimeout(300);
    await p.click(".lyrBtn"); await p.waitForTimeout(300); await p.locator('.lyrPanel [data-k="cnames"]').check(); await p.waitForTimeout(500); await shot("#map", "layers_panel"); await p.click(".lyrBtn");
    await p.locator('.lyrPanel [data-k="cnames"]').uncheck({ force: true }).catch(() => {});
    if (!process.env.NOML) {
      await p.evaluate(() => { map.jumpTo({ center: [6.05, 46.23], zoom: 6 }); }); await p.waitForTimeout(1500);
      const hit = await p.evaluate(() => { const f = map.queryRenderedFeatures({ layers: ["list"] }); if (!f.length) return null; const c = f.find(x => x.properties.n === 1) || f[0]; const xy = map.project(c.geometry.coordinates); const r = map.getContainer().getBoundingClientRect(); return [r.left + xy.x, r.top + xy.y]; });
      if (hit) { await p.mouse.click(hit[0], hit[1]); await p.waitForTimeout(1200); await shot("#atlas", "popup_cern"); } else errs.push(nm + ": no list sites rendered");
      const nf = await p.evaluate(() => [map.queryRenderedFeatures({ layers: ["list"] }).length]); console.log(nm, "list points rendered near CERN:", nf);
    } else {
      const c = p.locator("#map svg circle").first(); await c.click({ force: true }); await p.waitForTimeout(500); await shot("#atlas", "popup_fallback");
    }
    for (const c of ["countChart", "listYearChart", "typeChart", "listCountryChart", "spreadChart", "firstTable", "wdYearChart", "shareChart", "listTable"]) await shot("#" + c, c);
    if (nm === "phone" && !process.env.NOML) {
      await p.click("#theme"); await p.waitForTimeout(1200); await shot("#atlas", "dark_map"); await shot("#wdYearChart", "dark_wd");
      await p.locator("#atlas").scrollIntoViewIfNeeded(); await p.click(".mfs-btn"); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
      await p.click(".mfs-btn"); await p.waitForTimeout(600);
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
