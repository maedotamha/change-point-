import { chromium } from "playwright";
import path from "node:path";

const OUT_DIR = process.argv[2] || "../reports/images";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, colorScheme: "dark" });
await page.goto("http://localhost:5173/", { waitUntil: "networkidle" });
await page.waitForTimeout(1200);
await page.screenshot({ path: path.join(OUT_DIR, "dashboard_dark.png") });
console.log("Saved dashboard_dark.png");
await browser.close();
