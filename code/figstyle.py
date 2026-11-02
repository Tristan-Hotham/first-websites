"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the palette, and Natural Earth outlines in the Equal Earth projection. Reads only data/."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#636A72", "axes.labelcolor": "#1D2128",
                     "xtick.color": "#636A72", "ytick.color": "#636A72"})
BG, FG, MUT, LAND, RULE, SEA = "#F6F4EF", "#1D2128", "#636A72", "#E2DED3", "#DDD8CC", "#EAEEF0"
LINK, VISITED, HOT, GREY = "#1A3FD0", "#6B2FA0", "#C8322B", "#C9C3B8"
UNLIT = "#E2DED3"
TCOLS = [c for _, c in TYPES]; RCOLS = [c for _, c in REGIONS]

EE = Transformer.from_crs(4326, 8857, always_xy=True)
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    for ring in rings(f["geometry"]):
        x, y = EE.transform(np.clip(ring[:, 0], -179.9, 179.9), np.clip(ring[:, 1], -89.5, 89.5))
        SHAPES.append((f["properties"]["iso"], np.column_stack([x, y])))
WORLD_EXT = (-17.0e6, 17.0e6, -8.75e6, 8.7e6)


def world(ax, fills=None, alphas=None, edges=None, lw=.3, ext=WORLD_EXT, ec="#FFFFFF", land=UNLIT, z=1, skip_ata=True):
    """Countries, each filled from fills[iso] (else land), with alpha from alphas and an extra outline for isos in edges."""
    fills, alphas, edges = fills or {}, alphas or {}, edges or set()
    for iso, p in SHAPES:
        if skip_ata and iso == "ATA":
            continue
        ax.add_patch(MPoly(p, closed=True, fc=fills.get(iso, land), alpha=alphas.get(iso, 1), ec=ec, lw=lw, zorder=z))
    for iso, p in SHAPES:
        if iso in edges:
            ax.add_patch(MPoly(p, closed=True, fc="none", ec=FG, lw=1.0, zorder=z + .2))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")


def outline(ax, fc=None, lw=.8, ec=MUT, z=0):
    """Equal Earth globe outline."""
    lat = np.linspace(-90, 90, 181)
    xl, yl = EE.transform(np.full_like(lat, -180), lat); xr, yr = EE.transform(np.full_like(lat, 180), lat[::-1])
    ax.add_patch(MPoly(np.column_stack([np.r_[xl, xr], np.r_[yl, yr]]), closed=True, fc=fc or "none", ec=ec, lw=lw, zorder=z))


def proj(lon, lat):
    return EE.transform(np.asarray(lon), np.asarray(lat))


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def first_fills(R, S, upto=Y1):
    """Fill colour, alpha and list outline for the 'first recorded website' map."""
    fills, alphas, edges = {}, {}, set()
    for r in R["firsts"]["rows"]:
        if r["y"] > upto: continue
        fills[r["iso"]] = YCOL[r["y"] - Y0]
        if r["doubt"]: alphas[r["iso"]] = .42
        if r["src"] == "list": edges.add(r["iso"])
    return fills, alphas, edges
