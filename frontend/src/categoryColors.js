// Fixed categorical order (alphabetical) mapped to the palette's categorical
// slots. Never reassigned based on which categories are present in a given
// filter — identity stays fixed to the color.
export const CATEGORY_ORDER = [
  "Economic Shock",
  "Economic/Market",
  "Geopolitical Conflict",
  "Geopolitical Shock",
  "OPEC Policy",
  "Sanctions",
];

export const CATEGORY_COLORS = {
  "Economic Shock": "var(--series-1)",
  "Economic/Market": "var(--series-2)",
  "Geopolitical Conflict": "var(--series-3)",
  "Geopolitical Shock": "var(--series-4)",
  "OPEC Policy": "var(--series-5)",
  Sanctions: "var(--series-6)",
};

export const DEFAULT_CATEGORY_COLOR = "var(--text-muted)";
