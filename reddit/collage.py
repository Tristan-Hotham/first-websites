"""r/dataisbeautiful collage for first-websites: 2400 x 3200 px, light background. Numbers from data/results.json.
Map labels sit on open sea or on the paper around the globe, with a halo; leader lines never cross a label."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from shapely.geometry import shape as _shape, box as _box, Point as _Pt, LineString as _LS, Polygon as _Poly
from shapely.ops import unary_union, nearest_points
from shapely.prepared import prep as _prep
from shapely.validation import make_valid

R = jload(f"{DATA}/results.json"); S = jload(f"{DATA}/site.json")
L, WD, F, CC, E = R["list"], R["wd"], R["firsts"], R["cctld"], R["entries"]
BGc = "#F7F5F0"; SEAc = "#E9EFF2"
HALO = [pe.withStroke(linewidth=4, foreground=SEAc)]
HALOP = [pe.withStroke(linewidth=4, foreground=BGc)]
LIST = [dict(zip(S["list_cols"], r)) for r in S["list"]]
assert (F["cum_by_year"]["1992"], F["n"], L["n"]) == (7, 83, 119)

fig = plt.figure(figsize=(12, 16.0), dpi=200, facecolor=BGc)
fig.text(.045, .984, "The first websites", fontproperties=DISP, fontsize=46, color=FG, va="top")
fig.text(.045, .937, f"How the World Wide Web spread: from one server at CERN in December 1990 to {F['cum_by_year']['1992']} countries by 1992\n"
         f"and {F['n']} by 2000. Colour: the year of the earliest website recorded for each country.", fontproperties=SERP, fontsize=14.5, color=FG, va="top", linespacing=1.45)

# ---- map
ax = fig.add_axes([0, .505, 1, .405])
EXT = (-17.0e6, 17.0e6, -6.4e6, 10.4e6)
outline(ax, fc=SEAc, ec="#C9CDD0", lw=.8); fills, alphas, edges = first_fills(R, S); world(ax, fills, alphas, edges, lw=.3, ec=BGc, ext=EXT)
for r in LIST:
    if r["lat"] is None: continue
    x, y = proj(r["lon"], r["lat"]); ax.scatter([x], [y], s=16, c=TCOLS[r["type"]], ec="#fff", lw=.6, zorder=5)

_land = []
for f in jload(f"{GEO}/ne_50m_land.geojson")["features"]:
    g = _shape(f["geometry"]); gs = g.geoms if g.geom_type == "MultiPolygon" else [g]
    for q in gs:
        xy = np.array(q.exterior.coords); x, y = EE.transform(np.clip(xy[:, 0], -179.99, 179.99), np.clip(xy[:, 1], -89.9, 89.9))
        _land.append(make_valid(_Poly(np.column_stack([x, y]))))
LANDG = unary_union(_land).buffer(30e3); LANDP = _prep(LANDG)
fig.canvas.draw(); REN = fig.canvas.get_renderer()
PLACED, LINES = [], []


def tbox(t):
    bb = t.get_window_extent(REN)
    (x0, y0), (x1, y1) = ax.transData.inverted().transform([[bb.x0 - 4, bb.y0 - 3], [bb.x1 + 4, bb.y1 + 3]])
    return _box(x0, y0, x1, y1)


def bad(b):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    if not _box(x0 + 1e5, y0 + 1e5, x1 - 1e5, y1 - 1e5).contains(b): return True
    return LANDP.intersects(b) or any(b.intersects(o) for _, _, o in PLACED) or any(b.intersects(l) for _, l in LINES)


GRID = [(float(x), float(y)) for x in np.arange(-16.6e6, 16.7e6, 2.5e5) for y in np.arange(-6.2e6, 10.3e6, 2.0e5)]


def place(name, s, target, pref, ha="left", col=FG, size=9, w="medium"):
    """Every grid position in map metres (sea or paper), nearest to the preferred (lon, lat) first; keep the first clean one."""
    t = ax.text(0, 0, s, ha=ha, va="center", fontsize=size, color=col, family=MONO, linespacing=1.2, zorder=10, path_effects=HALO, fontweight=w)
    px, py = proj(*pref); px, py = float(px), float(py)
    tx, ty = proj(*target); c = _Pt(float(tx), float(ty))
    for x, y in sorted(GRID, key=lambda q: (q[0] - px) ** 2 + (q[1] - py) ** 2):
        t.set_position((x, y)); b = tbox(t)
        if bad(b): continue
        pb, _ = nearest_points(b, c); ln = _LS([(pb.x, pb.y), (c.x, c.y)])
        if any(ln.intersects(o) for _, _, o in PLACED) or any(ln.crosses(l) for _, l in LINES): continue
        PLACED.append((name, t, b)); LINES.append((name, ln)); ax.plot(*ln.xy, color=FG, lw=.7, zorder=9)
        return
    raise RuntimeError("no clean spot for " + name)


P = {r["n"]: r for r in LIST}
pt = lambda n: (P[n]["lon"], P[n]["lat"])
place("cern", "CERN, Dec 1990:\nthe first website", pt(1), (-30, 40), "center", col=YCOL[0], w="bold")
place("nikhef", "Nikhef, Feb 1992:\nthe third website", pt(4), (10, 88), "center")
place("cork", "Cork, Apr 1992:\nfirst in Ireland", pt(11), (-30, 88), "center")
place("slac", "SLAC, Dec 1991:\nfirst outside Europe", pt(3), (-140, 30), "center", col=YCOL[1], w="bold")
place("fnal", "Fermilab,\nJune 1992", pt(6), (-60, 42), "center")
place("huji", "Jerusalem, Apr 1992:\nfirst right to left", pt(12), (60, 5), "center")
place("kek", "KEK, Sept 1992:\nfirst in Japan", pt(16), (158, 30), "center")
for nm, t, b in PLACED:
    assert not LANDP.intersects(b) and not any(b.intersects(o) for n2, _, o in PLACED if n2 != nm), nm
for nm, l in LINES:
    assert not any(l.intersects(o) for n2, _, o in PLACED if n2 != nm), nm
print("labels ok:", len(PLACED))

# ---- legend under the map
lg = fig.add_axes([.06, .487, .42, .013]); lg.set_xlim(0, 11); lg.set_ylim(0, 1); lg.axis("off")
for k, c in enumerate(YCOL):
    lg.add_patch(Rectangle((k, 0), 1, 1, fc=c, ec=BGc, lw=.6))
    if k % 2 == 0: lg.text(k + .5, -.45, str(Y0 + k), ha="center", va="top", fontsize=9.5, color=FG)
lg.text(0, 1.5, "year of the earliest recorded website", fontsize=10.5, color=FG, va="bottom")
LP = SERP.copy(); LP.set_size(11.5)
fig.legend(handles=[Patch(fc=UNLIT, ec=MUT, lw=.5, label="no website recorded by 2000"), Patch(fc="none", ec=FG, lw=1.2, label="country in Wikipedia's pre-1995 list"),
                    Patch(fc=YCOL[3], alpha=.42, label="dated before the country's own domain (doubtful)")],
           loc="upper left", bbox_to_anchor=(.52, .506), ncol=1, frameon=False, prop=LP, labelspacing=.45)
fig.legend(handles=[Line2D([], [], ls="", marker="o", ms=8, mfc=c, mec="#fff", label=t) for t, c in TYPES], loc="upper left", bbox_to_anchor=(.035, .447),
           ncol=4, frameon=False, prop=LP, handletextpad=.3, columnspacing=1.0, title="dots: websites in the pre-1995 list, by kind", title_fontproperties=LP)

# ---- numbers row
nums = [(f"{L['n']}", YCOL[1], f"websites in Wikipedia's list\nof sites founded before 1995"),
        (f"{L['us_pct_known']:.0f}%", YCOL[4], f"of those with a known\ncountry were American"),
        (f"{F['n']}", YCOL[7], "countries with a website\nrecorded by 2000"),
        (f"{CC['by2000']}", "#636A72", "country code domains\n(.uk, .jp...) by 2000")]
for i, (big, col, small) in enumerate(nums):
    xx = .045 + i * .235
    fig.text(xx, .375, big, fontproperties=DISP, fontsize=36, color=col, va="top")
    fig.text(xx, .337, small, family=MONO, fontsize=10.5, color=FG, va="top", linespacing=1.4)

# ---- the list by year and kind
YT = L["year_type"]; ys = sorted(YT, key=int)
a = fig.add_axes([.075, .075, .38, .19]); a.set_facecolor(BGc)
for j, y in enumerate(ys):
    b = 0
    for k, t in enumerate(TN):
        v = YT[y][t]
        if v: a.bar(j, v, bottom=b, color=TCOLS[k], width=.66, ec=BGc, lw=.6); b += v
    a.text(j, b + 1.5, str(b), ha="center", fontsize=11, fontweight="medium")
a.set_xticks(range(4)); a.set_xticklabels(ys); a.set_ylim(0, 84); spines(a); a.tick_params(labelsize=10); a.grid(axis="y", color=RULE); a.set_axisbelow(True)
a.set_title("The pre-1995 list: physicists first,\nthen everybody (colours as the dots)", family=MONO, fontsize=12, color=FG, loc="left", pad=8)
a.text(-.4, 66, f"1991 to 1992: {L['sci_uni_9192']} of {L['n_9192']}\nlabs, universities\nand libraries", fontsize=9, color=FG, va="top", path_effects=HALOP)

# ---- spread
CY = {int(k): v for k, v in CC["cum"].items()}; FY = {int(k): v for k, v in F["cum_by_year"].items()}
b2 = fig.add_axes([.56, .075, .39, .19]); b2.set_facecolor(BGc)
b2.plot(list(CY), list(CY.values()), color=VISITED, lw=2.4, ls=(0, (6, 4)))
b2.plot(list(FY), list(FY.values()), color=LINK, lw=3)
b2.text(1999.6, CY[2000] + 8, f"{CY[2000]} with their\nown domain", ha="right", va="bottom", fontsize=9.5, color=VISITED, path_effects=HALOP)
b2.text(1999.8, 8, f"{FY[2000]} with a\nrecorded website", ha="right", va="bottom", fontsize=9.5, color=LINK, path_effects=HALOP)
b2.set_xlim(1985, 2000.5); b2.set_ylim(0, 260); spines(b2); b2.tick_params(labelsize=10); b2.grid(axis="y", color=RULE); b2.set_axisbelow(True)
b2.set_title("Countries reached: domains came first,\nwebsites followed", family=MONO, fontsize=12, color=FG, loc="left", pad=8)

fig.text(.045, .008, f"Sources: Wikipedia, 'List of websites founded before 1995' (coded by me: country, kind), 'History of the World Wide Web' (CC BY-SA 4.0); Wikidata\n"
         f"websites and country code domains (CC0; founding dates from 1993 for country firsts, as earlier ones are mostly organisations' founding); Natural Earth.\n"
         "'Earliest recorded in these sources', not the true first website. Chart: Tristan Hotham (Python, matplotlib) · maps.tristanhotham.com/first-websites",
         family=MONO, fontsize=8.2, color=MUT, linespacing=1.5, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "first_websites.png")
fig.savefig(out, facecolor=BGc, dpi=200)
print("ok", out)
