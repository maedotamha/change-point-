const BASE_URL = "http://127.0.0.1:5000";

async function getJSON(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${path} (${res.status})`);
  }
  return res.json();
}

export function fetchPrices(start, end) {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return getJSON(`/api/prices?${params.toString()}`);
}

export function fetchEvents(category) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  return getJSON(`/api/events?${params.toString()}`);
}

export function fetchEventCategories() {
  return getJSON("/api/events/categories");
}

export function fetchChangePoints() {
  return getJSON("/api/changepoints");
}

export function fetchSummary(start, end) {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return getJSON(`/api/summary?${params.toString()}`);
}
