import { chromium } from "playwright";
import path from "node:path";

const OUT_DIR = process.argv[2] || "../reports/images";
const URL = "http://localhost:5173/";

const viewports = [
  { name: "tablet", width: 834, height: 1100 },
  { name: "mobile", width: 390, height: 844 },
];

const browser = await chromium.launch();

for (const vp of viewports) {
  const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT_DIR, `dashboard_${vp.name}.png`), fullPage: true });
  console.log(`Saved dashboard_${vp.name}.png`);
  await page.close();
}

await browser.close();
