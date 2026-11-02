"""Header card, blog figures (release/blog/b_*.png, 1800 px wide) and paper figures (release/paper/f_*.png). Numbers
from data/results.json, places from data/site.json. Needs only data/."""
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from figstyle import *

R = jload(f"{DATA}/results.json"); S = jload(f"{DATA}/site.json")
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
os.makedirs(BL, exist_ok=True); os.makedirs(PA, exist_ok=True)
L, WD, F, CC = R["list"], R["wd"], R["firsts"], R["cctld"]
HALO = [pe.withStroke(linewidth=3.5, foreground=BG)]
FW = 12.0                                   # every figure is 12 inches wide: 1800 px in the blog, 2400 px in the paper


def both(fig, name, blog=True):
    fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    if blog:
        fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def ramp_legend(fig, x, y, w, h, title):
    ax = fig.add_axes([x, y, w, h]); ax.set_xlim(0, 11); ax.set_ylim(0, 1); ax.axis("off")
    for k, c in enumerate(YCOL):
        ax.add_patch(Rectangle((k, 0), 1, 1, fc=c, ec=BG, lw=.6))
        if k in (0, 2, 4, 6, 8, 10): ax.text(k + .5, -.35, str(Y0 + k), ha="center", va="top", fontsize=9, color=FG)
    ax.text(0, 1.35, title, fontsize=10, color=FG, va="bottom")


LIST = [dict(zip(S["list_cols"], r)) for r in S["list"]]

# ---------- map: first recorded website by country ----------
fig = plt.figure(figsize=(FW, 6.6), facecolor=BG); ax = fig.add_axes([0, .1, 1, .82])
outline(ax, fc=SEA, ec="#C9CDD0"); fills, alphas, edges = first_fills(R, S); world(ax, fills, alphas, edges, ec=BG)
for r in LIST:
    if r["lat"] is None: continue
    x, y = proj(r["lon"], r["lat"]); ax.scatter([x], [y], s=26, c=TCOLS[r["type"]], ec="#fff", lw=.7, zorder=5)
fig.text(.02, .955, f"Year of the earliest website recorded for each country, 1990 to 2000 ({F['n']} countries)\nDots: the {L['plotted']} placed websites of Wikipedia's pre-1995 list, coloured by kind as in the next figures", fontsize=10.5, color=FG, va="center", linespacing=1.4)
ramp_legend(fig, .03, .05, .3, .028, "first recorded website")
fig.legend(handles=[Patch(fc=UNLIT, ec=MUT, lw=.5, label="none recorded by 2000"), Patch(fc="none", ec=FG, lw=1, label="country in the pre-1995 list"),
                    Patch(fc=YCOL[3], alpha=.42, label="date before the country's own domain")],
           loc="lower center", bbox_to_anchor=(.66, .005), ncol=2, frameon=False, fontsize=9.5)
both(fig, "map")

# ---------- the list by year and kind ----------
YT = L["year_type"]; ys = sorted(YT, key=int)
fig = plt.figure(figsize=(FW, 5.4), facecolor=BG); ax = fig.add_axes([.07, .1, .55, .8]); ax.set_facecolor(BG)
for j, y in enumerate(ys):
    b = 0
    for k, t in enumerate(TN):
        v = YT[y][t]
        if v: ax.bar(j, v, bottom=b, color=TCOLS[k], width=.66, ec=BG, lw=.6); b += v
    ax.text(j, b + 1.2, str(b), ha="center", fontsize=12, fontweight="medium", color=FG)
ax.set_xticks(range(len(ys))); ax.set_xticklabels(ys); ax.set_ylim(0, 82); spines(ax); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
ax.set_ylabel("websites in the list")
fig.legend(handles=[Patch(color=c, label=t) for t, c in TYPES][::-1], loc="center left", bbox_to_anchor=(.65, .5), frameon=False, fontsize=10.5, title="kind of website (my coding)", title_fontsize=10.5)
both(fig, "list_years")

# ---------- kind and status ----------
TS = L["type_status"]; SC = [("live", "still online, says the list", LINK), ("gone", "closed or absorbed, says the list", HOT), ("unstated", "not stated", GREY)]
fig = plt.figure(figsize=(FW, 5.2), facecolor=BG); ax = fig.add_axes([.3, .24, .64, .72]); ax.set_facecolor(BG)
for k, t in enumerate(TN[::-1]):
    b = 0
    for s, n, c in SC:
        v = TS[t][s]; ax.barh(k, v, left=b, color=c, height=.62, ec=BG, lw=.6); b += v
    ax.text(b + .3, k, str(b), va="center", fontsize=10.5, fontweight="medium")
ax.set_yticks(range(len(TN))); ax.set_yticklabels(TN[::-1], fontsize=10.5); ax.tick_params(axis="y", length=0); spines(ax); ax.set_xlabel("websites in the list")
fig.legend(handles=[Patch(color=c, label=n) for s, n, c in SC], loc="lower center", bbox_to_anchor=(.6, 0), ncol=3, frameon=False, fontsize=10)
both(fig, "status")

# ---------- by country ----------
C = L["countries"] + [{"iso": "", "name": "Not known", "n": L["no_country"]}]
fig = plt.figure(figsize=(FW, 5.6), facecolor=BG); ax = fig.add_axes([.2, .06, .74, .86]); ax.set_facecolor(BG)
for k, c in enumerate(C[::-1]):
    col = GREY if not c["iso"] else RCOLS[0] if c["iso"] == "USA" else RCOLS[1] if S["cn"][c["iso"]][4] == "Europe" else RCOLS[2]
    ax.barh(k, c["n"], color=col, height=.66); ax.text(c["n"] + .6, k, str(c["n"]), va="center", fontsize=10)
ax.set_yticks(range(len(C))); ax.set_yticklabels([c["name"] for c in C[::-1]], fontsize=10.5); ax.tick_params(axis="y", length=0); spines(ax)
ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.legend(handles=[Patch(color=c, label=n) for n, c in REGIONS] + [Patch(color=GREY, label="no place in the text or known home")], loc="lower right", frameon=False, fontsize=10)
fig.text(.02, .955, f"Wikipedia's list of websites founded before 1995: {L['n']} websites by country ({L['us_pct_known']:.0f}% of those placed are American)", fontsize=11, color=FG)
both(fig, "countries")

# ---------- spread: countries with a website and with a domain ----------
CY = {int(k): v for k, v in CC["cum"].items()}; FY = {int(k): v for k, v in F["cum_by_year"].items()}
fig = plt.figure(figsize=(FW, 5.2), facecolor=BG); ax = fig.add_axes([.07, .11, .88, .8]); ax.set_facecolor(BG)
ax.plot(list(CY), list(CY.values()), color=VISITED, lw=2.6, ls=(0, (6, 4)), label="countries with their own country code domain (Wikidata dates)")
ax.plot(list(FY), list(FY.values()), color=LINK, lw=3.2, label="countries with a recorded website (pre-1995 list, Wikidata from 1993)")
ax.text(2000.2, CY[2000], str(CY[2000]), va="center", fontsize=11, color=VISITED); ax.text(2000.2, FY[2000], str(FY[2000]), va="center", fontsize=11, color=LINK)
for y, t in ((1990, "info.cern.ch"), (1992, f"{FY[1992]} countries")):
    ax.plot([y], [FY[y]], "o", color=LINK, ms=5); ax.text(y + (.15 if y == 1992 else 0), FY[y] + 9, t, ha="left" if y == 1992 else "center", fontsize=9.5, color=FG)
ax.set_xlim(1985, 2001.2); ax.set_ylim(0, 240); spines(ax); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.set_ylabel("countries")
ax.legend(loc="upper left", frameon=False, fontsize=10)
both(fig, "spread")

# ---------- Wikidata by year and region ----------
Yr = WD["years"]; keys = RN + ["unknown"]; cols = RCOLS + [GREY]
fig = plt.figure(figsize=(FW, 5.2), facecolor=BG); ax = fig.add_axes([.07, .11, .9, .74]); ax.set_facecolor(BG)
for d in Yr:
    b = 0
    for k, c in zip(keys, cols):
        ax.bar(d["y"], d[k], bottom=b, color=c, width=.72, alpha=.55 if d["y"] < STRICT_FLOOR else 1, ec=BG, lw=.5); b += d[k]
ax.text(1991, 95, "1990 to 1992:\nmostly founding dates\nof organisations", ha="center", fontsize=9.5, color=MUT)
ax.set_xticks(range(Y0, Y1 + 1)); spines(ax); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.set_ylabel("Wikidata websites founded")
fig.legend(handles=[Patch(color=c, label=n) for n, c in REGIONS] + [Patch(color=GREY, label="no country recorded")], loc="upper left", bbox_to_anchor=(.07, .99), ncol=4, frameon=False, fontsize=10)
both(fig, "wd_years")

# ---------- regional shares ----------
fig = plt.figure(figsize=(FW, 5.2), facecolor=BG); ax = fig.add_axes([.07, .11, .88, .74]); ax.set_facecolor(BG)
lr = {}
for y in (1991, 1992, 1993, 1994):
    rows = [r for r in LIST if r["year"] == y and r["iso"]]
    reg = lambda i: "United States" if i == "USA" else "Europe" if S["cn"][i][4] == "Europe" else "Rest of the world"
    lr[y] = [100 * sum(reg(r["iso"]) == n for r in rows) / len(rows) for n in RN]
for k, n in enumerate(RN):
    ax.plot([d["y"] for d in Yr], [d[n + "_pct"] for d in Yr], color=RCOLS[k], lw=2.4, label=f"{n}, Wikidata")
    ax.scatter(list(lr), [lr[y][k] for y in lr], marker="s", s=60, color=RCOLS[k], ec=BG, lw=1, zorder=4)
ax.set_xticks(range(Y0, Y1 + 1)); ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
spines(ax); ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.set_ylabel("share of the year's websites with a country")
fig.legend(handles=[Line2D([], [], color=c, lw=2.4, label=n) for n, c in REGIONS] + [Line2D([], [], ls="", marker="s", color=MUT, label="squares: the pre-1995 list")],
           loc="upper left", bbox_to_anchor=(.07, .99), ncol=4, frameon=False, fontsize=10)
both(fig, "share")

# ---------- how many websites (paper only) ----------
P = [(1990.97, 1, "1"), (1992.45, 10, "10"), (1992.95, 55, "50 to 60"), (1993.95, 623, "623"), (1994.45, 2738, "2,738"), (1995.45, 23500, "23,500")]
Q = [(1994.97, 2278, "2,278 (introduction)"), (1994.99, 10000, "more than 10,000 (1994 section)")]
fig = plt.figure(figsize=(FW, 4.6), facecolor=BG); ax = fig.add_axes([.08, .12, .88, .82]); ax.set_facecolor(BG)
ax.plot([p[0] for p in P], [p[1] for p in P], "-o", color=LINK, lw=2, ms=7)
for x, v, t in P: ax.text(x - .05, v * 1.35, t, ha="right", fontsize=10)
for x, v, t in Q: ax.plot([x], [v], "o", mfc=BG, mec=LINK, mew=2, ms=7); ax.text(x + .06, v, t, va="center", fontsize=9.5)
ax.set_yscale("log"); ax.set_ylim(.6, 60000); ax.set_xlim(1990.7, 1996.4); spines(ax); ax.grid(axis="y", color=RULE); ax.set_ylabel("websites in the world")
ax.set_xticks(range(1991, 1997))
both(fig, "counts", blog=False)

# ---------- header card 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.40, .14, .6, .8]); outline(ax, fc=SEA, ec="#C9CDD0", lw=.6); world(ax, fills, alphas, edges, lw=.2, ec=BG)
for r in LIST:
    if r["lat"] is None: continue
    x, y = proj(r["lon"], r["lat"]); ax.scatter([x], [y], s=9, c=TCOLS[r["type"]], ec="#fff", lw=.4, zorder=5)
ramp_legend(fig, .48, .1, .4, .03, "year of the first recorded website in each country")
fig.add_artist(Rectangle((.035, .84), .34, .07, transform=fig.transFigure, fc="#FFFEFA", ec="#CBC5B8", lw=1))
fig.text(.045, .875, "http://info.cern.ch/", fontsize=13, color=FG, va="center")
fig.text(.035, .78, "The", fontproperties=DISP, fontsize=54, color=FG, va="top")
fig.text(.035, .62, "first", fontproperties=DISP, fontsize=54, color=LINK, va="top")
fig.text(.035, .46, "websites", fontproperties=DISP, fontsize=54, color=VISITED, va="top")
for k, t in enumerate(["How the web spread, 1990 to 2000:", f"from one server at CERN to {F['n']} countries.", f"{L['us_pct_known']:.0f}% of the early sites in Wikipedia's list", "with a known country were American."]):
    fig.text(.035, .27 - k * .045, t, fontproperties=SERP, fontsize=14, color=FG, va="top")
fig.text(.035, .035, "maps.tristanhotham.com/first-websites", fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)
print("figures done", sorted(os.listdir(BL)), sorted(x for x in os.listdir(PA) if x.endswith(".png")))
