"""Builds the article figures from psu_data/. Usage: python3 make_figures.py"""
import csv, datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
BLUE, ORANGE, CRIT, GOOD = "#2a78d6", "#eb6834", "#d03b3b", "#0ca30c"
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED})

def load(name):
    rows = [r for r in csv.reader(open(f"psu_data/{name}.csv")) if len(r) >= 8]
    t = [dt.datetime.strptime(r[0].strip(), "%Y/%m/%d %H:%M:%S.%f") for r in rows]
    p = [float(r[1]) for r in rows]
    i0 = next(i for i, x in enumerate(p) if x > 150)
    i1 = max(i for i, x in enumerate(p) if x > 150)
    t0 = t[i0]
    return [(t[i] - t0).total_seconds() for i in range(i0, i1 + 1)], p[i0:i1 + 1]

def style(ax):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(length=0)

# ---- Figure 1: GPU power under load on the 750 W
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
tm, pm = load("psu_750w"); te, pe = load("psu_750w_recheck")
ax.plot(tm, pm, color=ORANGE, lw=1.1, label="750 W, morning run")
ax.plot(te, pe, color=BLUE, lw=1.1, label="750 W, evening run")
ax.axhline(430, color=CRIT, lw=1.6, ls=(0, (5, 3)))
ax.text(28, 441, "~430 W: where the 1200 W unit\nlost power (approx., from logs)", color=INK2, fontsize=10, va="bottom", linespacing=1.4)
ax.set_ylim(0, 620); ax.set_xlim(0, max(tm[-1], te[-1]))
ax.set_xlabel("Seconds since GPU load began"); ax.set_ylabel("GPU power draw (W)")
ax.set_title("The 750 W carried more than the 1200 W ever reached", loc="left", fontsize=14, fontweight="bold", color=INK, pad=22)
ax.text(0, 1.02, "RTX 5090, three 1,500-token generations, sampled every 100 ms. Evening run: 524 W average, 559 W peak.",
        transform=ax.transAxes, fontsize=9.5, color=INK2)
ax.legend(frameon=False, loc="lower right", fontsize=10, labelcolor=INK2)
style(ax); fig.tight_layout(); fig.savefig("figures/fig1_gpu_power_750w.png"); plt.close(fig)

# ---- Figure 2: every run on a timeline
D = dt.datetime(2026, 10, 18)
def T(s): h, m = map(int, s.split(":")); return D.replace(hour=h, minute=m)
runs = [("13:29", "750 W baseline", True), ("15:46", "Native cable #1, multi-rail", False),
 ("15:53", "Reseated 16-pin both ends", False), ("16:00", "Reseated again", False),
 ("16:35", "Second cable, other port", False), ("16:40", "Single-rail mode", False),
 ("16:45", "Smart plug removed", False), ("17:13", "PCIe Gen4", False),
 ("17:18", "One EPS cable, 0 RPM fan mode off", False), ("17:39", "Cable straightened", False),
 ("17:52", "4x8-pin adapter, 4 ports", False), ("17:56", "Adapter + single-rail", False),
 ("18:10", "750 W recheck", True), ("18:19", "24-pin reseated, disks removed", False),
 ("18:45", "750 W final", True)]
runs.sort(key=lambda r: T(r[0]))
fig, ax = plt.subplots(figsize=(10, 6.6), dpi=200)
for i, (t, label, ok) in enumerate(runs):
    y = len(runs) - 1 - i
    ax.plot([T(t)], [y], marker="o" if ok else "X", ms=10, color=GOOD if ok else CRIT, mec=SURFACE, mew=1.5, zorder=3)
    ax.text(T(t) + dt.timedelta(minutes=6), y, f"{t}  {label}", va="center", fontsize=9.5, color=INK2)
    ax.text(T("21:45"), y, "passed" if ok else "power lost", va="center", ha="right", fontsize=9, color=GOOD if ok else CRIT, fontweight="bold")
ax.set_xlim(T("13:10"), T("21:50")); ax.set_ylim(-0.8, len(runs) - 0.2); ax.set_yticks([])
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1)); ax.set_xticks([T(f"{h}:00") for h in range(14, 20)])
ax.set_title("Twelve changes on the 1200 W, twelve power cuts", loc="left", fontsize=14, fontweight="bold", color=INK, pad=22)
ax.text(0, 1.02, "Each run changed something new; none helped. The 750 W passed all three times. Cuts came 5-15 s into GPU load.",
        transform=ax.transAxes, fontsize=9.5, color=INK2)
style(ax); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID, lw=0.8)
fig.tight_layout(); fig.savefig("figures/fig2_run_timeline.png"); plt.close(fig)
print("ok")
