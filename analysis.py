"""Bangladesh's electricity: growth, gas dependence and the renewables gap.

Runs the SQL in sql/ with DuckDB, saves each result to results/ as CSV
and draws the charts in charts/. Run from the project folder:

    pip install -r requirements.txt
    python analysis.py
"""
from pathlib import Path
import re

import duckdb
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).parent
RESULTS, CHARTS = ROOT / "results", ROOT / "charts"
RESULTS.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

# Colours: validated categorical palette, Bangladesh always in slot 1 (blue).
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
PEER = "#a9a8a2"

if any("Inter" in f.name for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "Inter"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "font.size": 11,
})


def run_sql():
    con = duckdb.connect()
    con.execute((ROOT / "sql/01_load.sql").read_text())
    text = (ROOT / "sql/02_questions.sql").read_text()
    out = {}
    for name, query in re.findall(r"-- name: (\w+)\n(.*?;)", text, flags=re.S):
        df = con.execute(query).df()
        df.to_csv(RESULTS / f"{name}.csv", index=False)
        out[name] = df
    out["energy"] = con.execute("SELECT * FROM energy ORDER BY country, year").df()
    return out


def title(ax, headline, sub):
    ax.set_title(headline, loc="left", fontsize=14, fontweight="bold", color=INK, pad=26)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color=INK_2, va="bottom")


def source(fig):
    fig.text(0.01, 0.01, "Source: Our World in Data, energy and CO2 datasets (Ember, Energy Institute). Analysis: Md Jubair Imtiaj",
             fontsize=8.5, color=INK_2)


def chart_per_person(energy):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for country, g in energy.groupby("country"):
        bd = country == "Bangladesh"
        ax.plot(g.year, g.kwh_per_person, color=BLUE if bd else PEER, lw=2.6 if bd else 1.8, zorder=3 if bd else 2)
        last = g.dropna(subset=["kwh_per_person"]).iloc[-1]
        ax.text(last.year + 0.4, last.kwh_per_person, f"{country}  {last.kwh_per_person:,.0f}",
                va="center", fontsize=10.5, color=INK if bd else INK_2, fontweight="bold" if bd else "normal")
    ax.set_xlim(2000, 2029)
    ax.set_ylabel("kWh per person per year")
    title(ax, "Bangladesh generates the least electricity per person of the four",
          "Electricity generation per person, 2000–2025")
    source(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(CHARTS / "1_per_person.png", dpi=160)
    plt.close(fig)


def chart_bd_mix(mix):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    # Stack order keeps validated neighbours apart (orange never touches yellow).
    parts = [("gas", "Gas", BLUE), ("coal", "Coal", ORANGE),
             ("renewables", "Renewables", AQUA), ("oil", "Oil", YELLOW)]
    bottom = [0] * len(mix)
    for col, label, color in parts:
        vals = mix[col].clip(lower=0).tolist()
        ax.bar(mix.year, vals, bottom=bottom, color=color, width=0.78, label=label,
               edgecolor=SURFACE, linewidth=1.2)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for yr in (2010, 2025):
        row = mix[mix.year == yr].iloc[0]
        ax.text(yr, row.gas / 2, f"{row.gas:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    row = mix[mix.year == 2025].iloc[0]
    ax.text(2025, row.gas + row.coal / 2, f"{row.coal:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_xticks(range(2010, 2026, 3))
    ax.set_xlim(2009.4, 2025.6)
    ax.set_ylabel("% of electricity generated")
    ax.legend(ncol=4, frameon=False, loc="upper left", bbox_to_anchor=(0, -0.08), fontsize=10)
    title(ax, "Gas fell from 92% to 64% of Bangladesh's power; coal took its place",
          "Bangladesh electricity generation by source, 2010–2025")
    source(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(CHARTS / "2_bd_mix.png", dpi=160)
    plt.close(fig)


def chart_renewables(peers):
    peers = peers.sort_values("renewables_2025")
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    y = range(len(peers))
    for i, (_, r) in enumerate(peers.iterrows()):
        bd = r.country == "Bangladesh"
        c = BLUE if bd else INK_2
        ax.plot([r.renewables_2015, r.renewables_2025], [i, i], color=GRID, lw=3, zorder=1, solid_capstyle="round")
        ax.scatter(r.renewables_2015, i, s=70, color=SURFACE, edgecolor=c, linewidth=2, zorder=3)
        ax.scatter(r.renewables_2025, i, s=80, color=c, edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.text(r.renewables_2025 + 1.2, i, f"{r.renewables_2025:.0f}%", va="center", fontsize=10.5,
                color=INK, fontweight="bold" if bd else "normal")
    ax.set_yticks(list(y), peers.country, fontsize=11)
    ax.set_xlim(0, 52)
    ax.set_xlabel("Renewables, % of electricity generated   (○ 2015   ● 2025)")
    title(ax, "Bangladesh is stuck near 2% renewables while peers reach 24–45%",
          "Share of electricity from renewables (hydro, solar, wind, bioenergy), 2015 vs 2025")
    source(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHARTS / "3_renewables.png", dpi=160)
    plt.close(fig)


def chart_intensity(energy):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    e = energy[energy.year >= 2010]
    for country, g in e.groupby("country"):
        bd = country == "Bangladesh"
        ax.plot(g.year, g.g_co2_per_kwh, color=BLUE if bd else PEER, lw=2.6 if bd else 1.8, zorder=3 if bd else 2)
        last = g.dropna(subset=["g_co2_per_kwh"]).iloc[-1]
        nudge = {"Bangladesh": 14, "India": -14}.get(country, 0)
        ax.text(last.year + 0.3, last.g_co2_per_kwh + nudge, f"{country}  {last.g_co2_per_kwh:.0f}",
                va="center", fontsize=10.5, color=INK if bd else INK_2, fontweight="bold" if bd else "normal")
    ax.set_xlim(2010, 2028.5)
    ax.set_xticks(range(2010, 2026, 5))
    ax.set_ylim(0, 850)
    ax.set_ylabel("grams of CO2 per kWh")
    title(ax, "Bangladesh's power got slightly dirtier since 2015; all three peers got cleaner",
          "Carbon intensity of electricity generation, 2010–2025")
    source(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(CHARTS / "4_carbon_intensity.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    r = run_sql()
    chart_per_person(r["energy"])
    chart_bd_mix(r["q3_bd_mix"])
    chart_renewables(r["q4_peers"])
    chart_intensity(r["energy"])
    for name in ("q1_growth", "q2_bd_yoy", "q3_bd_mix", "q4_peers", "q5_emissions"):
        print(f"\n== {name}\n{r[name].to_string(index=False)}")
