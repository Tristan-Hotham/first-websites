"""Every number used anywhere (data/results.json), the reusable data tables (data/*.csv) and the page data (data/site.json).

Definitions:
  * the pre-1995 list: the {119} distinct websites in Wikipedia's "List of websites founded before 1995" (Chabad.org,
    listed under 1993 and 1994, counted once in 1993). Year = the year section it sits in. Country, place, kind and
    status are my reading of each entry (common.LIST); status counts only what the text says.
  * Wikidata websites: items typed as websites with an inception from 1990 to 2000, Usenet newsgroups left out.
    Inceptions before 1990 are the founding of the organisation behind the site (a newspaper, a society) and are only
    counted, never used as web dates. Country: Wikidata's country, else the country of the headquarters coordinates.
  * region: United States; Europe (Natural Earth's continent, so including Russia); rest of the world.
  * first recorded website in a country: the earliest of (a) the pre-1995 list (CERN dated 1990 from "History of the
    World Wide Web"), (b) Wikidata websites with an inception from 1993 on. Wikidata's 1990 to 1992 inceptions are left
    out of this one measure: those years hold far more items than the whole web had (see 'wd.early'), so they are mostly
    the founding of the organisation, not the site. It is the earliest recorded in these sources, not the true first.
  * ccTLD delegation: Wikidata's inception of the two-letter country code domain."""
import numpy as np, pandas as pd
from common import *

L0 = pd.read_pickle(f"{WORK}/list.pkl")
W0 = pd.read_pickle(f"{WORK}/wd.pkl")
CC = pd.read_pickle(f"{WORK}/cctld.pkl")
CHK = jload(f"{WORK}/checks.json")
CM = jload(f"{DATA}/countries.json")
cname = lambda i: CM[i]["name"] if isinstance(i, str) and i in CM else "Not stated"
pc = lambda a, b: round(100 * a / b, 1) if b else None
TI = {t: k for k, t in enumerate(TN)}
YRS = list(range(Y0, Y1 + 1))
MI = {m: k + 1 for k, m in enumerate("January February March April May June July August September October November December".split())}
R = {}

# ---------------- the pre-1995 list ----------------
L = L0[L0.dup == 0].copy()
L["month"] = L.when.map(lambda w: next((MI[m] for m in MI if m in w), 13))
L["region"] = L.iso.map(lambda i: None if not isinstance(i, str) else "United States" if i == "USA" else "Europe" if CM[i]["cont"] == "Europe" else "Rest of the world")
N = len(L)
assert N == 119
by_year = {int(y): int(n) for y, n in L.groupby("year").size().items()}
assert by_year == {1991: 3, 1992: 14, 1993: 28, 1994: 74}, by_year
ty = {t: int((L.type == t).sum()) for t in TN}
yt = {int(y): {t: int(((L.year == y) & (L.type == t)).sum()) for t in TN} for y in by_year}
cty = L.iso.fillna("none").value_counts()
known = L[L.iso.notna()]
st = L.status.replace("", "unstated").value_counts().to_dict()
R["list"] = {"n": N, "rows": int(CHK["list_rows"]), "by_year": by_year, "types": ty, "types_pct": {t: pc(v, N) for t, v in ty.items()},
             "year_type": yt, "n_countries": int(known.iso.nunique()), "no_country": int(L.iso.isna().sum()), "known": len(known),
             "countries": [{"iso": i, "name": cname(i if i != "none" else None), "n": int(v)} for i, v in cty.items() if i != "none"],
             "us": int((L.iso == "USA").sum()), "us_pct_known": pc((L.iso == "USA").sum(), len(known)), "us_pct": pc((L.iso == "USA").sum(), N),
             "europe": int((L.region == "Europe").sum()), "europe_pct_known": pc((L.region == "Europe").sum(), len(known)),
             "rest": int((L.region == "Rest of the world").sum()), "rest_pct_known": pc((L.region == "Rest of the world").sum(), len(known)),
             "gbr": int((L.iso == "GBR").sum()), "irl": int((L.iso == "IRL").sum()), "che": int((L.iso == "CHE").sum()), "can": int((L.iso == "CAN").sum()),
             "live": int(st.get("live", 0)), "gone": int(st.get("gone", 0)), "unstated": int(st.get("unstated", 0)),
             "live_pct": pc(st.get("live", 0), N), "gone_pct": pc(st.get("gone", 0), N), "unstated_pct": pc(st.get("unstated", 0), N),
             "plotted": int(L.lat.notna().sum()), "basis": L.basis.replace("", "none").value_counts().to_dict(),
             "type_status": {t: {s: int(((L.type == t) & (L.status.replace("", "unstated") == s)).sum()) for s in ("live", "gone", "unstated")} for t in TN},
             "sci_uni_9192": int(L[L.year <= 1992].type.isin(TN[:2]).sum()), "n_9192": int((L.year <= 1992).sum()),
             "com_9394": int(L[L.year >= 1993].type.isin([TN[2]]).sum()), "n_9394": int((L.year >= 1993).sum()),
             "sci_uni_94": int(L[L.year == 1994].type.isin(TN[:2]).sum()), "n_94": by_year[1994],
             "us_1994": int(((L.year == 1994) & (L.iso == "USA")).sum()), "us_1994_pct": pc(((L.year == 1994) & (L.iso == "USA")).sum(), by_year[1994]),
             "us_9192": int(((L.year <= 1992) & (L.iso == "USA")).sum())}
Ls = R["list"]
Ls["fun_94"] = yt[1994][TN[7]]
Ls["us_share_by_year"] = {int(y): pc(((L.year == y) & (L.iso == "USA")).sum(), ((L.year == y) & L.iso.notna()).sum()) for y in by_year}
Ls["top_type"] = max(ty, key=ty.get); Ls["top_type_n"] = ty[Ls["top_type"]]
Ls["sci_uni_9192_pct"] = pc(Ls["sci_uni_9192"], Ls["n_9192"]); Ls["sci_uni_94_pct"] = pc(Ls["sci_uni_94"], Ls["n_94"])
Ls["countries_list"] = ", ".join(c["name"] for c in Ls["countries"])
assert Ls["countries"][0]["iso"] == "USA" and Ls["countries"][1]["iso"] == "GBR"
assert Ls["n_countries"] == 14 and Ls["no_country"] == 13
# entries the text relies on
T = {r.n: r for r in L0.itertuples()}
R["entries"] = {k: {"title": T[n].title, "when": T[n].when, "year": int(T[n].year)} for k, n in
                (("cern", 1), ("vlib", 2), ("slac", 3), ("nikhef", 4), ("fnal", 6), ("curia", 11), ("huji", 12), ("kek", 16), ("cybergrass", 17),
                 ("tech", 32), ("expasy", 42), ("jumpstation", 28), ("coffee", 43), ("imdb", 24), ("wired", 45), ("cordis", 67),
                 ("radio_prague", 100), ("ezln", 120), ("fogcam", 72), ("whitehouse", 117), ("yahoo", 119), ("bbc", 56), ("amnesty", 49),
                 ("barney", 55), ("irish_times", 81), ("cdnair", 61), ("joachim", 27), ("principia", 40), ("in2p3", 10), ("ntt", 36))}

# ---------------- how many websites there were (the article's own counts) ----------------
R["web_counts"] = {"jun1992": 10, "end1992": "fifty to sixty", "end1993": 623, "mid1994": 2738, "end1994_intro": 2278, "end1994_sec": "more than 10,000",
                   "jun1995": 23500, "pre1995": 2879}
R["web_counts"]["list_share_pct"] = pc(N, R["web_counts"]["pre1995"])

# ---------------- Wikidata websites ----------------
W0 = W0.copy()
pre = W0[W0.y < WEB_FLOOR]
W = W0[(W0.y >= WEB_FLOOR) & (W0.y <= Y1) & (W0.newsgroup == 0)].copy()
bah = W0[W0.label == "Buenos Aires Herald"].iloc[0]
assert bah.y == 1876
yr = []
for y in YRS:
    a = W[W.y == y]
    row = {"y": y, "n": len(a), "known": int(a.iso.notna().sum())}
    for r_ in RN: row[r_] = int((a.region == r_).sum())
    row["unknown"] = int(a.iso.isna().sum())
    for r_ in RN: row[r_ + "_pct"] = pc(row[r_], row["known"])
    row["plus_known"] = int(a.iso_plus.notna().sum())
    for r_ in RN: row[r_ + "_plus_pct"] = pc((a.region_plus == r_).sum(), row["plus_known"])
    yr.append(row)
Y = pd.DataFrame(yr).set_index("y")
kn = W[W.iso.notna()]
early = W[W.y <= 1992]
R["wd"] = {"rows": CHK["wd_rows"], "items": CHK["wd_items"], "pre1990": len(pre), "pre1990_pct": pc(len(pre), CHK["wd_items"]),
           "newsgroups": len(CHK["wd_newsgroups"]), "n": len(W), "years": yr,
           "country": int(W.iso.notna().sum()), "country_pct": pc(W.iso.notna().sum(), len(W)),
           "country_p17": int((W.co_src == "P17").sum()), "country_hq": int((W.co_src == "HQ").sum()),
           "coords": int(W.lat.notna().sum()), "coords_pct": pc(W.lat.notna().sum(), len(W)),
           "en": int((W.en != "").sum()), "en_pct": pc((W.en != "").sum(), len(W)), "url": int((W.url != "").sum()), "url_pct": pc((W.url != "").sum(), len(W)),
           "n_countries": int(W.iso.nunique()), "us": int((W.iso == "USA").sum()), "us_pct": pc((W.iso == "USA").sum(), len(kn)),
           "europe": int((W.region == "Europe").sum()), "europe_pct": pc((W.region == "Europe").sum(), len(kn)),
           "rest": int((W.region == "Rest of the world").sum()), "rest_pct": pc((W.region == "Rest of the world").sum(), len(kn)),
           "top": [{"iso": i, "name": cname(i), "n": int(v)} for i, v in kn.iso.value_counts().head(15).items()],
           "early": len(early), "y1990": int(Y.loc[1990, "n"]), "y1994": int(Y.loc[1994, "n"]), "y1995": int(Y.loc[1995, "n"]),
           "y1999": int(Y.loc[1999, "n"]), "y2000": int(Y.loc[2000, "n"]), "peak_year": int(Y.n.idxmax()), "peak_n": int(Y.n.max()),
           "since1995": int(Y.loc[1995:].n.sum()), "since1995_pct": pc(Y.loc[1995:].n.sum(), len(W)),
           "bah_year": int(bah.y), "oldest_label": pre.sort_values("date").iloc[0].label, "oldest_year": int(pre.y.min()),
           "url_extra": int((W.iso.isna() & W.url_iso.notna()).sum()), "plus_known": int(W.iso_plus.notna().sum())}
wd = R["wd"]
wd["no_country"] = int(W.iso.isna().sum())
wd["us_min_pct"] = float(Y["United States_pct"].min()); wd["us_max_pct"] = float(Y["United States_pct"].max())
wd["us_min_year"] = int(Y["United States_pct"].idxmin()); wd["us_max_year"] = int(Y["United States_pct"].idxmax())
plusk = W[W.iso_plus.notna()]
wd["plus_us_pct"] = pc((plusk.region_plus == "United States").sum(), len(plusk)); wd["plus_europe_pct"] = pc((plusk.region_plus == "Europe").sum(), len(plusk))
wd["plus_rest_pct"] = pc((plusk.region_plus == "Rest of the world").sum(), len(plusk))
for a, b in ((1990, 1994), (1995, 2000)):
    s = kn[(kn.y >= a) & (kn.y <= b)]
    for r_ in RN:
        wd[f"{r_.split()[0].lower()}_{a}_{b}_pct"] = pc((s.region == r_).sum(), len(s))
    wd[f"known_{a}_{b}"] = len(s)
assert wd["peak_year"] in (1999, 2000) and wd["early"] > 100        # many more 1990 to 1992 items than websites existed

# ---------------- first recorded website in each country ----------------
cand = []
for r in L[L.iso.notna()].itertuples():
    y = 1990 if r.n == 1 else int(r.year)
    cand.append({"iso": r.iso, "y": y, "m": 12 if r.n == 1 else r.month, "src": "list", "name": r.title, "when": r.when, "url": (r.hosts[0] if r.hosts else ""),
                 "wiki": r.wiki, "ref": f"https://en.wikipedia.org/wiki/List_of_websites_founded_before_1995#{r.hid}", "order": r.n})
for r in W[W.iso.notna() & (W.y >= STRICT_FLOOR)].itertuples():
    yo = r.date.endswith("-01-01")
    cand.append({"iso": r.iso, "y": int(r.y), "m": 13 if yo else int(r.date[5:7]), "src": "wikidata", "name": r.label, "when": r.date[:4] if yo else r.date,
                 "url": r.url, "wiki": r.en.replace("https://en.wikipedia.org/wiki/", ""), "ref": f"https://www.wikidata.org/wiki/{r.Q}", "order": 1000})
CA = pd.DataFrame(cand).sort_values(["iso", "y", "m", "order"])
F = CA.drop_duplicates("iso").copy()
F["same_year"] = F.apply(lambda r: int(((CA.iso == r.iso) & (CA.y == r.y)).sum()), axis=1)
F["name_c"] = F.iso.map(cname); F["cont"] = F.iso.map(lambda i: CM[i]["cont"])
# a flag, not a filter: a Wikidata first dated before the country's own domain existed is probably the founding of the
# organisation (a newspaper, a broadcaster), not of its website
CCY = {r.iso: int(r.y) for r in CC[CC.y.notna()].itertuples()}
for i, t in PRED.items():                    # a predecessor domain (.su, .yu, .an, .cs) counts as the country's own
    CCY[i] = min(CCY.get(i, 9999), int(CHK["cc_pred"][t][:4]))
F["doubt"] = [int(s_ == "wikidata" and i in CCY and y < CCY[i]) for s_, i, y in zip(F.src, F.iso, F.y)]
F = F.sort_values(["y", "m", "order", "name_c"]).reset_index(drop=True)
# the effect of the stricter floor: Wikidata alone with the 1990 floor
lax = W[W.iso.notna()].sort_values("date").drop_duplicates("iso")
fy = F.groupby("y").size()
R["firsts"] = {"n": len(F), "n_1994": int((F.y <= 1994).sum()), "n_1992": int((F.y <= 1992).sum()), "n_list": int((F.src == "list").sum()),
               "n_wd": int((F.src == "wikidata").sum()), "new_by_year": {int(y): int(fy.get(y, 0)) for y in YRS},
               "cum_by_year": {int(y): int(fy[fy.index <= y].sum()) for y in YRS},
               "lax_1990_1992": int((lax.y <= 1992).sum()), "lax_n": len(lax), "no_record": int(len(CM) - len(F)),
               "rows": [{"iso": r.iso, "country": r.name_c, "y": int(r.y), "name": r.name, "when": r.when, "src": r.src, "url": r.url, "wiki": r.wiki,
                         "ref": r.ref, "same_year": int(r.same_year), "cont": r.cont, "doubt": int(r.doubt)} for r in F.itertuples()]}
fr = R["firsts"]
fr["n_doubt"] = int(F.doubt.sum()); fr["doubt_names"] = ", ".join(F[F.doubt == 1].name_c)
fr["peak_new_year"] = int(fy.idxmax()); fr["peak_new_n"] = int(fy.max())
fr["by_iso"] = {r["iso"]: r for r in fr["rows"]}
FI = fr["by_iso"]
assert FI["CHE"]["y"] == 1990 and FI["USA"]["y"] == 1991 and FI["JPN"]["y"] == 1992 and FI["IRL"]["y"] == 1992 and FI["ISR"]["y"] == 1992
cont_first = F.sort_values(["y", "m", "order"]).drop_duplicates("cont")
fr["continents"] = [{"cont": r.cont, "country": r.name_c, "y": int(r.y), "name": r.name, "src": r.src} for r in cont_first.itertuples()]
fr["by_cont"] = {c["cont"]: c for c in fr["continents"]}
cc2 = F[F.doubt == 0].sort_values(["y", "m", "order"]).drop_duplicates("cont")
fr["by_cont_clean"] = {r.cont: {"country": r.name_c, "y": int(r.y), "name": r.name, "src": r.src} for r in cc2.itertuples()}
fr["by_cont_n"] = {c: int((F.cont == c).sum()) for c in F.cont.unique()}
fr["cont_total"] = {c: sum(1 for v in CM.values() if v["cont"] == c) for c in F.cont.unique()}
# countries with no record by 2000, weighted by population
pop = {i: CM[i]["pop"] for i in CM}
fr["pop_covered_pct"] = pc(sum(pop[i] for i in F.iso), sum(pop.values()))
fr["africa_n"] = int((F.cont == "Africa").sum()); fr["africa_total"] = sum(1 for v in CM.values() if v["cont"] == "Africa")

# ---------------- ccTLDs ----------------
CCd = CC[CC.y.notna()].copy(); CCd["y"] = CCd.y.astype(int)
cy = {y: int((CCd.y <= y).sum()) for y in range(1985, Y1 + 1)}
R["cctld"] = {"items": CHK["cc_items"], "with_date": CHK["cc_with_date"], "matched": len(CC), "matched_dated": len(CCd),
              "first": CCd.sort_values("date").iloc[0].tld, "first_date": CCd.sort_values("date").iloc[0].date,
              "by1989": cy[1989], "by1990": cy[1990], "by1994": cy[1994], "by2000": cy[Y1], "cum": cy,
              "new_by_year": {y: int((CCd.y == y).sum()) for y in range(1985, Y1 + 1)}, "after2000": int((CCd.y > Y1).sum()),
              "wiki_rows": CHK["cc_wiki_rows"], "wiki_with_year": CHK["cc_wiki_with_year"], "both": CHK["cc_both"], "agree": CHK["cc_agree"],
              "disagree": [[t, int(a), b] for t, a, b in CHK["cc_disagree"]]}
cc_ = R["cctld"]
cc_["peak_year"] = max(cc_["new_by_year"], key=cc_["new_by_year"].get); cc_["peak_n"] = cc_["new_by_year"][cc_["peak_year"]]
CCi = CCd.set_index("iso")
gap = []
for r in F.itertuples():
    if r.iso in CCY:
        gap.append(int(r.y) - CCY[r.iso])
gap = np.array(gap)
gl = np.array([int(r.y) - CCY[r.iso] for r in F[F.src == "list"].itertuples() if r.iso in CCY])
cc_["gap_list_median"] = float(np.median(gl)); cc_["gap_list_min"] = int(gl.min()); cc_["gap_list_max"] = int(gl.max()); cc_["gap_list_n"] = len(gl)
cc_["gap_n"] = len(gap); cc_["gap_median"] = float(np.median(gap)); cc_["web_before_tld"] = int((gap < 0).sum()); cc_["same_year"] = int((gap == 0).sum())
cc_["us_date"] = CCi.loc["USA", "date"]; cc_["gb_date"] = CCi.loc["GBR", "date"]; cc_["ch_y"] = int(CCi.loc["CHE", "y"]); cc_["jp_y"] = int(CCi.loc["JPN", "y"])
MN = "January February March April May June July August September October November December".split()
cc_["us_month"] = f"{MN[int(cc_['us_date'][5:7]) - 1]} {cc_['us_date'][:4]}"
cc_["by_iso"] = {i: {"tld": r.tld, "y": int(r.y), "date": r.date} for i, r in CCi.iterrows()}
assert cc_["first"] == ".us" and cc_["first_date"].startswith("1985")

# ---------------- milestones (History of the World Wide Web and the list) ----------------
R["milestones"] = [
    {"date": "12 November 1990", "what": "Berners-Lee and Cailliau's formal proposal for the WorldWideWeb hypertext project"},
    {"date": "20 December 1990", "what": "info.cern.ch, the first website, published at CERN"},
    {"date": "January 1991", "what": "the first web servers outside CERN switched on"},
    {"date": "6 August 1991", "what": "Berners-Lee posts a summary of the project to the alt.hypertext newsgroup"},
    {"date": "12 December 1991", "what": "SLAC in California: the first web server outside Europe"},
    {"date": "June 1992", "what": "ten websites, according to the list's introduction"},
    {"date": "30 April 1993", "what": "CERN puts the web in the public domain, free to anyone"},
    {"date": "End of 1993", "what": "623 websites (Matthew Gray's count)"},
    {"date": "June 1995", "what": "some 23,500 websites"}]

R["source"] = {"revids": CHK["revids"], "fetched": FETCHED, "list_rows": CHK["list_rows"], "wd_rows": CHK["wd_rows"], "wd_items": CHK["wd_items"],
               "cc_rows": CHK["cc_rows"], "n_ne": len(CM)}
R["defs"] = {"web_floor": WEB_FLOOR, "strict_floor": STRICT_FLOOR,
             "cc_disagree": "; ".join(f"{t} ({a} in Wikidata, {b} in Wikipedia)" for t, a, b in cc_["disagree"])}
R["meta"] = {"page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "slug": SLUG}

# ---------------- data tables ----------------
out = L0.copy()
out["counted"] = (out.dup == 0).astype(int)
out["country"] = out.iso.map(lambda i: cname(i) if isinstance(i, str) else "")
out["wikipedia"] = out.wiki.map(lambda w: f"https://en.wikipedia.org/wiki/{w}" if w else "")
out["list_section"] = out.hid.map(lambda h: f"https://en.wikipedia.org/wiki/List_of_websites_founded_before_1995#{h}")
out["hosts"] = out.hosts.map(lambda h: " ".join(h))
out["place_basis"] = out.basis.map({"text": "named in the list", "org": "organisation's home (my assignment)", "country": "country only", "": "not known"})
out["status"] = out.status.replace("", "not stated")
out[["n", "title", "year", "when", "counted", "type", "iso", "country", "place", "lat", "lon", "place_basis", "status", "hosts", "wikipedia", "list_section"]] \
    .rename(columns={"n": "order_in_article", "title": "name", "year": "list_year", "when": "date_in_text", "iso": "iso3"}).to_csv(f"{DATA}/pre1995_list.csv", index=False)
wo = W.copy(); wo["country"] = wo.iso.map(lambda i: cname(i) if isinstance(i, str) else "")
wo[["Q", "label", "date", "y", "iso", "country", "co_src", "region", "lat", "lon", "url", "en"]] \
    .rename(columns={"Q": "wikidata_id", "date": "inception", "y": "year", "iso": "iso3", "co_src": "country_from", "en": "english_wikipedia"}) \
    .to_csv(f"{DATA}/wikidata_websites_1990_2000.csv", index=False)
pre[["Q", "label", "date", "iso"]].rename(columns={"Q": "wikidata_id", "date": "inception", "iso": "iso3"}).sort_values("inception").to_csv(f"{DATA}/wikidata_inception_before_1990.csv", index=False)
F[["iso", "name_c", "cont", "y", "when", "name", "src", "url", "wiki", "ref", "same_year", "doubt"]] \
    .rename(columns={"iso": "iso3", "name_c": "country", "cont": "continent", "y": "year", "when": "date", "name": "website", "src": "source",
                     "wiki": "wikipedia_article", "ref": "source_link", "same_year": "records_that_year", "doubt": "dated_before_national_domain"}).assign(cctld_year=lambda d: d.iso3.map(lambda i: cc_["by_iso"].get(i, {}).get("y"))) \
    .to_csv(f"{DATA}/first_website_by_country.csv", index=False)
CC.assign(country=CC.iso.map(cname)).rename(columns={"iso": "iso3", "date": "wikidata_inception", "y": "year", "wiki_year": "wikipedia_year_registered"}) \
    [["tld", "iso3", "country", "wikidata_inception", "year", "wikipedia_year_registered"]].to_csv(f"{DATA}/cctld_delegation.csv", index=False)
yy = pd.DataFrame(yr)
yy["list"] = yy.y.map(lambda y: by_year.get(y, 0)); yy["new_countries"] = yy.y.map(fr["new_by_year"]); yy["countries_cum"] = yy.y.map(fr["cum_by_year"])
yy["cctld_cum"] = yy.y.map(cy)
yy[["y", "n", "known", "United States", "Europe", "Rest of the world", "unknown", "list", "new_countries", "countries_cum", "cctld_cum"]] \
    .rename(columns={"y": "year", "n": "wikidata_websites", "known": "wikidata_with_country", "unknown": "wikidata_no_country",
                     "list": "pre1995_list", "new_countries": "countries_first_recorded", "countries_cum": "countries_with_a_record", "cctld_cum": "cctlds_delegated"}) \
    .to_csv(f"{DATA}/websites_by_year.csv", index=False)

# ---------------- page data ----------------
LI = [[int(r.n), r.title, int(r.year), r.iso if isinstance(r.iso, str) else "", None if np.isnan(r.lat) else r.lat, None if np.isnan(r.lon) else r.lon,
       TI[r.type], r.status, r.when, (r.hosts[0] if r.hosts else ""), r.wiki, r.hid, r.basis] for r in L.itertuples()]
WI = [[r.Q, r.label, int(r.y), r.iso if isinstance(r.iso, str) else "", None if np.isnan(r.lat) else round(r.lat, 3), None if np.isnan(r.lon) else round(r.lon, 3),
       r.url, r.en.replace("https://en.wikipedia.org/wiki/", ""), r.date] for r in W.sort_values("date").itertuples()]
site = {"ycol": YCOL, "types": TYPES, "regions": REGIONS, "list_cols": ["n", "name", "year", "iso", "lat", "lon", "type", "status", "when", "host", "wiki", "hid", "basis"],
        "list": LI, "wd_cols": ["q", "name", "year", "iso", "lat", "lon", "url", "wiki", "date"], "wd": WI,
        "firsts": {r["iso"]: [r["y"], r["name"], r["src"], r["url"], r["wiki"], r["when"], r["ref"], r["same_year"], r["doubt"]] for r in fr["rows"]},
        "cctld": {i: [v["tld"], v["y"], v["date"]] for i, v in cc_["by_iso"].items()},
        "cn": {i: [v["name"], v["lx"], v["ly"], v["pop"], v["cont"]] for i, v in CM.items()}}
jsave(site, f"{DATA}/site.json")
R["firsts"].pop("by_iso"); R["cctld"].pop("by_iso")
R["firsts"]["by_iso"] = {r["iso"]: {"y": r["y"], "name": r["name"], "src": r["src"]} for r in fr["rows"]}
jsave(R, f"{DATA}/results.json", indent=1)
print("list", by_year, ty, "\n status", st, "countries", Ls["n_countries"], Ls["countries_list"])
print("wd", {k: wd[k] for k in ("n", "pre1990", "country_pct", "coords_pct", "us_pct", "europe_pct", "rest_pct", "early", "plus_us_pct", "url_extra")})
print("shares 90-94 / 95-00", {k: v for k, v in wd.items() if "_199" in k or "_2000" in k})
print("firsts", fr["n"], fr["new_by_year"], "lax 90-92", fr["lax_1990_1992"], "list", fr["n_list"], fr["continents"])
print("cctld", {k: cc_[k] for k in ("matched_dated", "by1989", "by1990", "by1994", "by2000", "peak_year", "peak_n", "gap_median", "web_before_tld", "gap_n")})
print({k: os.path.getsize(f"{DATA}/{k}") // 1024 for k in ("site.json", "results.json")})
