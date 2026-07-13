"""Render the Markdown reports to PDF using reportlab.

Generates:
  - reports/interim_report.pdf   (from reports/interim_report.md, with images)
  - docs/analysis_workflow.pdf
  - docs/assumptions_and_limitations.pdf
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle,
    HRFlowable,
)

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "reports" / "images"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1B", parent=styles["Heading1"], spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1f4e79")))
styles.add(ParagraphStyle(name="H2B", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1f4e79")))
styles.add(ParagraphStyle(name="H3B", parent=styles["Heading3"], spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#2f6b3a")))
styles.add(ParagraphStyle(name="BodyB", parent=styles["BodyText"], spaceAfter=8, leading=14))
styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=8.5, textColor=colors.grey, spaceAfter=12, leading=11))
styles.add(ParagraphStyle(name="TitleB", parent=styles["Title"], textColor=colors.HexColor("#1f4e79")))
styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], textColor=colors.grey, spaceAfter=14))

TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
])

Q = "&quot;"  # safe quote entity, used for emphasis quotes inside paragraph text


def hr():
    return HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cccccc"), spaceBefore=4, spaceAfter=10)


def para(text, style="BodyB"):
    return Paragraph(text, styles[style])


def image(path, max_width=6.5 * inch):
    img = RLImage(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = max_width
    img.drawHeight = max_width * ratio
    return img


def build_interim_report():
    doc = SimpleDocTemplate(
        str(ROOT / "reports" / "interim_report.pdf"),
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="Interim Report - Change Point Analysis of Brent Oil Prices",
        author="Birhan Energies",
    )
    s = []
    s.append(para("Interim Report - Change Point Analysis of Brent Oil Prices", "TitleB"))
    s.append(para("Birhan Energies | Task 1 Deliverable | 13 Jul 2026", "Meta"))
    s.append(hr())

    s.append(para("1. Business Context", "H1B"))
    s.append(para(
        "Birhan Energies is analysing how major political and economic events - conflicts in "
        "oil-producing regions, international sanctions, and OPEC policy decisions - have shaped "
        "Brent crude oil prices, to support investment, policy, and operational decisions. This report "
        "covers Task 1: the analysis workflow, a structured events dataset, and initial exploratory "
        "findings on the price series."
    ))

    s.append(para("2. Planned Analysis Steps (summary)", "H1B"))
    steps = [
        "Load and clean the daily Brent price series (20-May-1987 to 14-Nov-2022).",
        "Exploratory analysis: trend, stationarity, volatility (this report).",
        "Compile a structured dataset of major events (data/events.csv, 17 events).",
        "Build a Bayesian change point model in PyMC (discrete-uniform prior on switch point "
        "<i>tau</i>, before/after means, pm.math.switch, Normal likelihood); run MCMC via pm.sample().",
        "Check convergence (r_hat, trace plots), identify the change point from the posterior of "
        "<i>tau</i>, and quantify the shift in price level.",
        "Associate detected change points with researched events and report quantified, "
        "hypothesis-framed impact statements.",
        "Build a Flask + React dashboard exposing prices, change points, and event correlations (Task 3).",
    ]
    for i, step in enumerate(steps, 1):
        s.append(para(f"{i}. {step}"))
    s.append(para(
        "Full detail: <i>docs/analysis_workflow.md</i>. Assumptions, limitations, and the "
        "correlation-vs-causation discussion: <i>docs/assumptions_and_limitations.md</i>."
    ))

    s.append(para("3. Events Dataset", "H1B"))
    s.append(para(
        "data/events.csv contains 17 major events (1990-2022) spanning geopolitical conflicts, "
        "OPEC policy decisions, sanctions, and economic shocks, each with an approximate start date, "
        "category, description, and expected price direction - e.g. Iraq's invasion of Kuwait "
        "(1990-08-02), the 2014 OPEC decision not to cut output, the 2020 Saudi-Russia price war, and "
        "Russia's invasion of Ukraine (2022-02-24). This list will be cross-referenced against detected "
        "change points in Task 2."
    ))

    s.append(para("4. Initial EDA Findings", "H1B"))
    s.append(para(
        "<b>Dataset:</b> 9,011 daily observations, 20-May-1987 to 14-Nov-2022. Price range "
        "$9.10-$143.95/barrel (mean $48.42, std $32.86)."
    ))

    s.append(para("4.1 Trend", "H2B"))
    s.append(para(
        "The raw series (Fig. 1) shows multiple distinct regimes rather than one stable trend: a calm "
        "period below ~$25/bbl through the late 1990s; a sustained uptrend from 2002 peaking near "
        "$147/bbl in mid-2008; the 2008 financial-crisis crash; a 2011-2014 plateau around "
        "$105-125/bbl; the late-2014 OPEC-driven collapse; a COVID-19 crash to single digits in "
        "April 2020; and the 2022 spike following Russia's invasion of Ukraine."
    ))
    s.append(image(IMG_DIR / "01_price_series.png"))
    s.append(para(
        "<i>Figure 1. Brent crude oil daily price, 1987-2022. Vertical structure visibly aligns "
        "with major shocks (1990-91 Gulf War, 2008 financial crisis, 2014 OPEC glut, 2020 "
        "COVID-19, 2022 Ukraine invasion).</i>",
        "Caption",
    ))

    s.append(para("4.2 Stationarity", "H2B"))
    table_data = [
        ["Series", "ADF p-value", "KPSS p-value", "Conclusion"],
        ["Price level", "0.289", "0.010", "Non-stationary"],
        ["Log return", "~ 0.000", "0.100", "Stationary"],
    ]
    t = Table(table_data, colWidths=[1.6 * inch, 1.4 * inch, 1.4 * inch, 1.8 * inch])
    t.setStyle(TABLE_STYLE)
    s.append(t)
    s.append(Spacer(1, 10))
    s.append(para(
        "Price levels fail to reject the ADF unit-root null and reject the KPSS stationarity null "
        "- consistent with the visible trending/regime behaviour. Log returns are stationary on "
        "both tests. <b>Implication:</b> a change point model applied to price levels detects shifts in "
        "the mean price level (regime shifts), which is the quantity of direct business interest; log "
        "returns are the right series for any future volatility-regime or ARIMA/GARCH work."
    ))

    s.append(para("4.3 Volatility", "H2B"))
    s.append(para(
        "Log returns (Fig. 2) show clear <b>volatility clustering</b> - large swings bunch "
        "together in time around 1990-91, 2008-09, 2014-16, and 2020, rather than "
        "being spread uniformly - and a 30-day rolling standard deviation (Fig. 3) makes these "
        "high-volatility windows explicit. The return distribution (Fig. 4) is strongly fat-tailed "
        "(excess kurtosis ~ 66) and left-skewed (skew ~ -1.74): large negative shocks "
        "are more extreme and more frequent than large positive ones."
    ))
    s.append(image(IMG_DIR / "02_log_returns.png"))
    s.append(para("<i>Figure 2. Daily log returns, showing volatility clustering.</i>", "Caption"))
    s.append(image(IMG_DIR / "03_rolling_volatility.png"))
    s.append(para("<i>Figure 3. 30-day rolling standard deviation of log returns.</i>", "Caption"))
    s.append(image(IMG_DIR / "04_distributions.png"))
    s.append(para("<i>Figure 4. Distribution of price levels (left) vs. log returns (right).</i>", "Caption"))

    s.append(para("4.4 Modeling Implications", "H2B"))
    s.append(para(
        "- Non-stationary price levels + multiple visible regimes -> a <b>change point model "
        "on price levels</b> (not a single global mean/trend model) is the right tool to identify "
        "structural breaks.<br/>"
        "- Fat-tailed, clustered volatility -> a Normal likelihood is a reasonable starting "
        "point for the Task 2 mean-shift model, with a Student-t likelihood and/or explicit "
        "volatility-regime (Markov-switching) modeling as a natural extension."
    ))
    s.append(para(
        "Full reproducible analysis: <i>notebooks/eda.ipynb</i> (executed, with outputs) and "
        "<i>scripts/eda.py</i>."
    ))

    s.append(para("5. Assumptions and Limitations (summary)", "H1B"))
    s.append(para(
        "Event dates are approximate; the model assumes a locally constant mean around each break; "
        "and - critically - a detected change point is a <b>statistical correlation in "
        "time</b>, not proof that a specific event caused the shift. See "
        "<i>docs/assumptions_and_limitations.md</i> for the full discussion, including what would be "
        "required to move from correlation to a causal claim (plausible mechanism, ruling out "
        "confounders, counterfactual/control-series reasoning)."
    ))

    doc.build(s)
    print("Wrote reports/interim_report.pdf")


def build_workflow_doc():
    doc = SimpleDocTemplate(
        str(ROOT / "docs" / "analysis_workflow.pdf"),
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="Analysis Workflow - Brent Oil Change Point Analysis",
        author="Birhan Energies",
    )
    s = []
    s.append(para("Analysis Workflow", "TitleB"))
    s.append(para("Brent Oil Change Point Analysis | Birhan Energies | Task 1", "Meta"))
    s.append(hr())

    s.append(para("1. Objective", "H1B"))
    s.append(para(
        "Quantify how major geopolitical events, OPEC decisions, and economic shocks are associated "
        "with structural shifts in Brent crude oil prices (daily, 20-May-1987 to 14-Nov-2022), and "
        "communicate the findings to investors, policymakers, and energy companies."
    ))

    s.append(para("2. Planned Analysis Steps", "H1B"))
    steps = [
        ("Data loading and cleaning", "parse data/BrentOilPrices.csv, standardise the mixed date formats, sort chronologically, check for gaps/duplicates."),
        ("Exploratory data analysis", "plot the raw price series; compute and plot log returns log(price_t) - log(price_(t-1)); test stationarity (ADF, KPSS) on both series; examine volatility clustering via rolling standard deviation. <i>(Completed - see notebooks/eda.ipynb and reports/interim_report.pdf.)</i>"),
        ("Event research and compilation", "compile a structured list of 15+ major events (wars, sanctions, OPEC decisions, financial crises) with approximate start dates into data/events.csv. <i>(Completed.)</i>"),
        ("Bayesian change point modeling (Task 2)", "build a PyMC model with a discrete-uniform prior over the switch point tau, separate " + Q + "before" + Q + " and " + Q + "after" + Q + " mean parameters (mu_1, mu_2), a pm.math.switch function linking tau to the active mean, and a Normal likelihood. Run MCMC via pm.sample()."),
        ("Convergence and posterior diagnostics", "check r_hat ~ 1.0 via pm.summary(), inspect trace plots (pm.plot_trace()), and plot the posterior distribution of tau to assess how sharply the change point is localised in time."),
        ("Event association", "map the posterior mode of tau (and any additional change points from extended/multiple-change-point models) to the nearest entries in data/events.csv, and formulate hypotheses about which event(s) plausibly triggered each detected shift."),
        ("Impact quantification", "for each associated change point, report the before/after posterior means, the absolute and percentage change, and a probabilistic statement (e.g. " + Q + "P(mu_2 &gt; mu_1) = 0.98" + Q + ")."),
        ("Dashboard (Task 3)", "expose the price series, change point results, and event correlations via a Flask API, and build a React frontend with filtering, event highlighting, and drill-down."),
        ("Reporting", "write the final report (blog-post format) with embedded visualisations, quantified impact statements, limitations, and future work."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        s.append(para(f"{i}. <b>{title}</b> - {desc}"))

    s.append(para("3. Communication Channels", "H1B"))
    table_data = [
        ["Audience", "Channel / Format"],
        ["Internal team / tutors", "Slack #all-week10, GitHub issues and project board for task tracking"],
        ["Investors / analysts", "Interactive dashboard (Task 3) for self-service exploration of price vs. events"],
        ["Policymakers / government bodies", "Written report (PDF / Medium-style blog post) with plain-language, quantified impact statements and visualisations"],
        ["Energy companies (operational planning)", "Summary tables of historical regime shifts and their magnitude/duration, delivered alongside the dashboard"],
    ]
    wrapped = [[Paragraph(c, styles["BodyB"]) for c in row] for row in table_data]
    t = Table(wrapped, colWidths=[2.1 * inch, 4.9 * inch])
    t.setStyle(TABLE_STYLE)
    s.append(t)

    s.append(para("4. References", "H1B"))
    s.append(para(
        "See the project README.md for the full reading list (Bayesian change point detection, PyMC "
        "documentation, MCMC background) used to inform the modeling approach in Task 2."
    ))

    doc.build(s)
    print("Wrote docs/analysis_workflow.pdf")


def build_assumptions_doc():
    doc = SimpleDocTemplate(
        str(ROOT / "docs" / "assumptions_and_limitations.pdf"),
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="Assumptions and Limitations",
        author="Birhan Energies",
    )
    s = []
    s.append(para("Assumptions and Limitations", "TitleB"))
    s.append(para("Brent Oil Change Point Analysis | Birhan Energies", "Meta"))
    s.append(hr())

    s.append(para("Assumptions", "H1B"))
    assumptions = [
        "<b>Event dates are approximate " + Q + "start dates" + Q + "</b> for each entry in data/events.csv. Real-world events (wars, sanctions regimes, OPEC policy shifts) unfold over days to months; a single date is a simplification used to align events with the daily price series.",
        "<b>Brent price is treated as a single global benchmark.</b> We do not adjust for inflation, currency effects (all prices are nominal USD/barrel), or the fact that Brent, WTI, and OPEC basket prices can diverge during regional supply shocks.",
        "<b>A mean-shift change point model is an adequate first approximation.</b> We assume that, locally around a structural break, the price process can be summarised by a constant mean plus noise. This is a simplification - markets also exhibit trends, mean-reversion, and volatility regimes that a single-mean-shift model does not capture.",
        "<b>One (or a small, fixed number of) change point(s) are estimated at a time</b> for interpretability. In reality, the 35-year series plausibly contains dozens of regime shifts; the model is extended incrementally rather than fit with an unbounded number of change points in the first pass.",
        "<b>The trading calendar</b> (holidays, weekends, exchange closures) is not explicitly modeled. Gaps between consecutive trading days are treated as if they were of equal length.",
    ]
    for a in assumptions:
        s.append(para(f"- {a}"))

    s.append(para("Limitations", "H1B"))
    limitations = [
        "<b>Correlation in time is not proof of causation.</b> This is the central methodological caveat of the whole analysis and is expanded on below.",
        "<b>Data does not capture magnitude of an event.</b> data/events.csv records that an event occurred and a qualitative expected direction, not a quantitative measure of its severity, so the strength of any detected shift cannot be directly attributed to " + Q + "how big" + Q + " the event was.",
        "<b>Multiple plausible causes can coincide.</b> Oil markets are influenced by simultaneous macro factors (currency moves, demand shocks, OPEC policy, and geopolitical events can overlap within days of each other), which makes it difficult to isolate a single " + Q + "cause" + Q + " for an inferred change point.",
        "<b>Change point models detect breaks in the modeled parameter only</b> (e.g. the mean). They do not, by themselves, explain why the break occurred - that step always requires the analyst to bring in outside context (the event list) and reason qualitatively about plausibility and timing.",
        "<b>Look-ahead / hindsight bias risk.</b> Because the event list is compiled with the benefit of hindsight, there is a risk of confirmation bias when matching change points to events. We mitigate this by requiring temporal proximity (the event should precede or coincide with, not follow, the detected shift) and by being explicit that these are hypotheses, not proven causal claims.",
    ]
    for l in limitations:
        s.append(para(f"- {l}"))

    s.append(para("Correlation vs. Causal Impact", "H1B"))
    s.append(para(
        "A Bayesian change point model identifies a date (or a posterior distribution over dates) at "
        "which the statistical properties of the price series most likely shifted, and it quantifies "
        "that shift (e.g., the change in mean price). This is fundamentally a <b>descriptive, "
        "correlational</b> result: it tells us when the data-generating process changed and by how much."
    ))
    s.append(para(
        "It does <b>not</b>, on its own, establish that a specific real-world event caused that shift. "
        "To move from correlation to a causal claim one would need, at minimum:"
    ))
    reqs = [
        "<b>Temporal precedence</b> - the event must precede the change point, not follow it (we check this, but proximity alone is weak evidence).",
        "<b>A plausible mechanism</b> - an economic/geopolitical channel by which the event could move the balance of oil supply, demand, or risk premium.",
        "<b>Ruling out confounders</b> - other events, seasonal effects, or macroeconomic shifts occurring in the same window that could equally explain the change.",
        "<b>Counterfactual reasoning or a natural-experiment design</b> (e.g. difference-in-differences, synthetic control, or event-study methods with a control series) to estimate what prices would have done absent the event - something a single-series change point model cannot provide.",
    ]
    for r in reqs:
        s.append(para(f"- {r}"))
    s.append(para(
        "Throughout this project we therefore frame event associations as <b>hypotheses consistent "
        "with the evidence</b> (" + Q + "the detected change point around [date] is temporally consistent "
        "with [event], and a price shift in the [direction] implied by the event's likely "
        "supply/demand effect" + Q + "), not as proven causal statements."
    ))

    doc.build(s)
    print("Wrote docs/assumptions_and_limitations.pdf")


if __name__ == "__main__":
    build_interim_report()
    build_workflow_doc()
    build_assumptions_doc()
