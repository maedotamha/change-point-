import { chromium } from "playwright";
import path from "node:path";

const OUT_DIR = process.argv[2] || "../reports/images";
const URL = "http://localhost:5173/";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

const errors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});
page.on("pageerror", (err) => errors.push(String(err)));

await page.goto(URL, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);

await page.screenshot({ path: path.join(OUT_DIR, "dashboard_full.png"), fullPage: true });
console.log("Saved dashboard_full.png");

// Click on an event in the sidebar to test drill-down
const firstEvent = page.locator(".event-item").first();
await firstEvent.click();
await page.waitForTimeout(1000);
await page.screenshot({ path: path.join(OUT_DIR, "dashboard_drilldown.png"), fullPage: true });
console.log("Saved dashboard_drilldown.png");

// Test category filter
const opecFilter = page.locator(".legend-item", { hasText: "OPEC Policy" });
await opecFilter.click();
await page.waitForTimeout(800);
await page.screenshot({ path: path.join(OUT_DIR, "dashboard_filtered.png") });
console.log("Saved dashboard_filtered.png");

console.log("Console errors:", JSON.stringify(errors, null, 2));

await browser.close();
