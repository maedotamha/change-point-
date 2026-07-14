import { useMemo } from "react";
import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { CATEGORY_COLORS, DEFAULT_CATEGORY_COLOR } from "../categoryColors";

const MS_PER_YEAR = 365.25 * 24 * 3600 * 1000;

// Recharts' default numeric-axis ticks don't know our formatter collapses
// many timestamps to the same label (e.g. many months all read as "1990").
// We generate an explicit, span-appropriate tick set instead so labels
// never repeat or crowd together.
function computeTicks(startTs, endTs) {
  const spanYears = (endTs - startTs) / MS_PER_YEAR;
  const ticks = [];
  const startYear = new Date(startTs).getFullYear();
  const endYear = new Date(endTs).getFullYear();

  if (spanYears > 15) {
    const first = Math.ceil(startYear / 5) * 5;
    for (let y = first; y <= endYear; y += 5) ticks.push(new Date(y, 0, 1).getTime());
  } else if (spanYears > 6) {
    const first = Math.ceil(startYear / 2) * 2;
    for (let y = first; y <= endYear; y += 2) ticks.push(new Date(y, 0, 1).getTime());
  } else if (spanYears > 2) {
    for (let y = startYear; y <= endYear; y += 1) ticks.push(new Date(y, 0, 1).getTime());
  } else {
    const stepMonths = spanYears > 1 ? 3 : 1;
    const d = new Date(startTs);
    d.setDate(1);
    while (d.getTime() <= endTs) {
      ticks.push(d.getTime());
      d.setMonth(d.getMonth() + stepMonths);
    }
  }
  return ticks.filter((t) => t >= startTs && t <= endTs);
}

function makeTickFormatter(spanYears) {
  return (ts) => {
    const d = new Date(ts);
    if (spanYears > 2) return d.getFullYear().toString();
    return d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
  };
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;

  const pricePoint = payload.find((p) => p.dataKey === "price");
  const eventPoint = payload.find((p) => p.dataKey === "flagY");

  return (
    <div className="chart-tooltip">
      {eventPoint && eventPoint.payload && (
        <>
          <div className="chart-tooltip-title">{eventPoint.payload.event}</div>
          <div className="chart-tooltip-row">
            <span
              className="tooltip-key"
              style={{ background: CATEGORY_COLORS[eventPoint.payload.category] || DEFAULT_CATEGORY_COLOR }}
            />
            <span className="tooltip-label">{eventPoint.payload.category}</span>
          </div>
          <div className="chart-tooltip-row">
            <strong>{eventPoint.payload.date}</strong>
          </div>
        </>
      )}
      {pricePoint && !eventPoint && (
        <>
          <div className="chart-tooltip-title">{pricePoint.payload.date}</div>
          <div className="chart-tooltip-row">
            <span className="tooltip-key" style={{ background: "var(--price-line)" }} />
            <span className="tooltip-label">Price</span>
            <strong className="tooltip-value">${pricePoint.value.toFixed(2)}</strong>
          </div>
        </>
      )}
    </div>
  );
}

export default function PriceChart({ prices, events, changePoints, onEventClick, highlightedEventDate }) {
  const chartData = useMemo(() => {
    if (!prices || !prices.dates) return [];
    return prices.dates.map((d, i) => ({
      ts: new Date(d).getTime(),
      date: d,
      price: prices.prices[i],
    }));
  }, [prices]);

  const maxPrice = useMemo(
    () => (chartData.length ? Math.max(...chartData.map((d) => d.price)) : 100),
    [chartData]
  );
  const minPrice = useMemo(
    () => (chartData.length ? Math.min(...chartData.map((d) => d.price)) : 0),
    [chartData]
  );

  const flagY = maxPrice * 1.08;
  const yDomain = [Math.max(0, minPrice * 0.9), maxPrice * 1.18];

  const domainStart = chartData.length ? chartData[0].ts : 0;
  const domainEnd = chartData.length ? chartData[chartData.length - 1].ts : 1;
  const spanYears = (domainEnd - domainStart) / MS_PER_YEAR;
  const xTicks = useMemo(() => computeTicks(domainStart, domainEnd), [domainStart, domainEnd]);
  const tickFormatter = useMemo(() => makeTickFormatter(spanYears), [spanYears]);

  const eventPoints = useMemo(() => {
    if (!events) return [];
    return events
      .map((e) => ({
        ts: new Date(e.Date).getTime(),
        date: e.Date,
        event: e.Event,
        category: e.Category,
        flagY,
      }))
      .filter((e) => e.ts >= domainStart && e.ts <= domainEnd);
  }, [events, flagY, domainStart, domainEnd]);

  return (
    <ResponsiveContainer width="100%" height={440}>
      <ComposedChart data={chartData} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid stroke="var(--gridline)" strokeDasharray="0" vertical={false} />
        <XAxis
          dataKey="ts"
          type="number"
          scale="time"
          domain={[domainStart, domainEnd]}
          ticks={xTicks}
          tickFormatter={tickFormatter}
          stroke="var(--baseline)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
        />
        <YAxis
          domain={yDomain}
          tickFormatter={(v) => `$${v}`}
          stroke="var(--baseline)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
          width={56}
        />
        <Tooltip content={<CustomTooltip />} />

        {changePoints.map((cp) => (
          <ReferenceLine
            key={cp.date}
            x={new Date(cp.date).getTime()}
            stroke="var(--text-primary)"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{
              value: cp.date.slice(0, 7),
              position: "top",
              fill: "var(--text-secondary)",
              fontSize: 10,
              angle: -90,
              offset: 12,
            }}
          />
        ))}

        <Line
          type="monotone"
          dataKey="price"
          stroke="var(--price-line)"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />

        <Scatter
          dataKey="flagY"
          data={eventPoints}
          shape={(props) => {
            const { cx, cy, payload } = props;
            const isHighlighted = highlightedEventDate === payload.date;
            const color = CATEGORY_COLORS[payload.category] || DEFAULT_CATEGORY_COLOR;
            return (
              <g
                style={{ cursor: "pointer" }}
                onClick={() => onEventClick && onEventClick(payload)}
              >
                <circle cx={cx} cy={cy} r={16} fill="transparent" />
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHighlighted ? 7 : 5}
                  fill={color}
                  stroke="var(--surface-1)"
                  strokeWidth={2}
                />
              </g>
            );
          }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
