"""Read the four Wikipedia articles, the Wikidata websites and ccTLD tables, and Natural Earth countries; clean each.

1. The pre-1995 list. The article is prose: a level-2 heading for each year (1991, 1992, 1993, 1994) and under it a
   level-3 heading and a short paragraph for each website. I split it on those headings, keep the heading, the year of
   its section, the paragraph text, the first Wikipedia link in the paragraph, and any host names the text writes out
   (www.example.com, sito.org...). The country, place, kind and status of each entry are my reading of the text
   (common.LIST); each 'still online' or 'gone' status must be backed by a phrase that appears in that entry
   (common.STATUS_EVIDENCE). Chabad.org appears twice (1993 and 1994) and is counted once, in 1993.
2. Wikidata websites. One row per combination of values, so I collapse to one row per item: the earliest inception, the
   country (the Natural Earth country containing the headquarters point where there is one, which overrides Wikidata's
   own country where the two disagree; otherwise Wikidata's first country), the first headquarters point, the
   first official URL and the English Wikipedia article. Inceptions before 1990 cannot be web launches (the first website
   went up in December 1990); I treat them as the founding of the organisation behind the site and keep them only to
   count them. Usenet newsgroups typed as websites are dropped.
3. Country code top-level domains. Wikidata's ccTLD items with their inception (taken as the date the domain was
   created, that is delegated) and country; matched to Natural Earth countries by the two-letter code (with .uk for the
   United Kingdom). The Wikipedia ccTLD table's "Year registered" column, where filled, is kept as a cross-check.
4. Facts quoted from "History of the World Wide Web" and the list's introduction are checked against the text."""
import html as _html
import numpy as np, pandas as pd
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

WP = jload(f"{RAW}/wiki_pages.json")
chk = {"revids": {k: WP[k]["revid"] for k in WP}}

# ---------------- Natural Earth countries: Wikidata ids, ISO codes, shapes ----------------
NE = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
Q2ISO, A2ISO, GEOMS, GISO, CONT, NAME = {}, {}, [], [], {}, {}
for f in NE:
    p = f["properties"]; iso = NE_FIX.get(iso_of(p), iso_of(p))
    if p.get("WIKIDATAID"): Q2ISO.setdefault(p["WIKIDATAID"], iso)
    a2 = p.get("ISO_A2_EH") if p.get("ISO_A2_EH") not in ("-99", None) else p.get("ISO_A2")
    if a2 and a2 != "-99": A2ISO.setdefault(a2.lower(), iso)
    CONT.setdefault(iso, p["CONTINENT"]); NAME.setdefault(iso, (p.get("NAME_EN") or p["NAME"]).replace("People's Republic of China", "China").replace("United States of America", "United States"))
    GEOMS.append(shape(f["geometry"])); GISO.append(iso)
Q2ISO.update(WD_COUNTRY_FIX)
TREE = STRtree(GEOMS)


def pip(lon, lat):
    pt = Point(lon, lat)
    for k in TREE.query(pt):
        if GEOMS[k].contains(pt): return GISO[k]
    k = TREE.nearest(pt)            # coastal points that fall just offshore of the simplified 1:50m outline
    return GISO[k] if GEOMS[k].distance(pt) < 0.25 else None


# ---------------- 1. the pre-1995 list ----------------
h = WP[LIST_TITLE]["html"]
h = re.sub(r"<style.*?</style>|<sup.*?</sup>", "", h, flags=re.S)
h = re.sub(r'<span class="mw-editsection.*?</span></span>', "", h, flags=re.S)
h = h[:h.index('id="See_also"')]
intro = wtext(h[:h.index('id="1991_websites"')])
parts = re.split(r'<h([23]) id="([^"]*)">(.*?)</h[23]>', h)
MON = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = rf"((?:{MON}) \d{{1,2}}, 199\d|(?:{MON}) (?:of )?199\d|(?:early|late|mid|fall|spring|summer|autumn|winter|the fall|the summer|the spring)(?: of)? 199\d)"
rows, year, yintro = [], None, {}
for i in range(1, len(parts), 4):
    lvl, hid, title, body = parts[i], parts[i + 1], parts[i + 2], parts[i + 3]
    title = _html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
    if lvl == "2":
        year = int(title[:4]); yintro[year] = wtext(body); continue
    body = body.split('<div class="mw-heading')[0]
    n = len(rows) + 1
    link = ""                       # the link in the paragraph whose text matches the heading
    for a, at in re.findall(r'<a href="/wiki/([^"#]+)"[^>]*>(.*?)</a>', body, flags=re.S):
        an, tn = norm(wtext(at)), norm(title)
        if an and (an == tn or tn in an or an in tn):
            link = a; break
    link = WIKI_FIX.get(n, link)
    t = wtext(body)
    dates = re.findall(DATE_RE, t)
    when = WHEN_FIX[n] if n in WHEN_FIX else (dates[0] if dates else "")
    when = re.sub(r"^(\w+) (\d{1,2}), (\d{4})$", r"\2 \1 \3", when).replace("the ", "").replace("fall of", "autumn").replace("fall", "autumn")
    hosts = re.findall(r"\b((?:www\.|[a-z0-9-]+\.)+(?:com|org|net|gov|edu|uk|ie|ch|lu|cz|eu|ca|mit\.edu|ntt|einet)(?:/[\w./-]*)?)", t)
    hosts = [x.rstrip("./") for x in hosts if x != "co.uk"]
    rows.append({"n": n, "year": year, "title": title, "hid": hid, "text": t, "wiki": link, "when": when, "hosts": list(dict.fromkeys(hosts))})
assert [r["year"] for r in rows].count(1991) == 3 and len(rows) == len(LIST) == 120, (len(rows), len(LIST))
L = pd.DataFrame(rows)
cur = pd.DataFrame(LIST, columns=["n", "iso", "place", "basis", "tk", "status"])
assert list(cur.n) == list(range(1, 121))
L = L.merge(cur, on="n")
L["type"] = L.tk.map(TK)
spaced = lambda s: re.sub(r"\s+", "", s).lower()
for n, ph in STATUS_EVIDENCE.items():
    assert spaced(ph) in spaced(L.loc[L.n == n, "text"].iloc[0]), (n, ph)
assert set(L[L.status != ""].n) == set(STATUS_EVIDENCE), set(L[L.status != ""].n) ^ set(STATUS_EVIDENCE)
for n, d in LIST_DUP.items():
    assert L.loc[L.n == n, "title"].iloc[0] == L.loc[L.n == d, "title"].iloc[0] == "Chabad.org"
L["dup"] = L.n.isin(LIST_DUP).astype(int)
assert L.place.dropna().isin(PLACES).all(), set(L.place.dropna()) - set(PLACES)
L["lat"] = L.place.map(lambda p: PLACES[p][0] if isinstance(p, str) else np.nan); L["lon"] = L.place.map(lambda p: PLACES[p][1] if isinstance(p, str) else np.nan)
# the curated place and country must agree with the Natural Earth outline
for r in L[L.lat.notna()].itertuples():
    assert pip(r.lon, r.lat) == r.iso, (r.n, r.title, pip(r.lon, r.lat), r.iso)
# checks of the facts the text uses, entry by entry
T = dict(zip(L.n, L.text))
assert "first web server in North America on December 12, 1991" in T[3]
assert "third website in the world in February 1992" in T[4]
assert "first in Ireland" in T[11] and "April 1992" in T[11] and "ninth web server in the world" in T[11]
assert "tenth website to go online" in T[12] and "first RTL website" in T[12]
assert "first web page in Japan" in T[16] and "September 1992" in T[16]
assert "launched in October 1994" in T[45] and "first webcam" in T[43] and "world's first Web search engine" in T[28]
assert "European Commission 's first permanent website" in T[67] and "www.cordis.lu" in T[67]
assert "first newspaper in Ireland" in T[81] and "first newspaper to deliver content over the Web" in T[32]
assert "Czech Republic" in T[100] and "Chiapas" in T[120] and "Norway" in T[27] and "Wales" in T[24]
assert "Switzerland" in T[1] and "Illinois" in T[6] and "Scotland" in T[28] and "Minnesota" in T[70]
assert "oldest still-operating webcam" in T[72] and "first website for an airline" in T[61]
chk["list_rows"] = len(L); chk["list_unique"] = int((L.dup == 0).sum())
# the list's introduction and year notes (counts of all websites at the time, as the article gives them)
for s in ("created in August 1991 by Tim Berners-Lee at CERN", "By June 1992, there were ten websites", "623 by the end of the year",
          "By the end of 1994, the total number of websites was 2,278", "some 23,500 sites", "Of the 2,879 websites established before 1995"):
    assert s in intro, s
assert "fifty to sixty websites" in yintro[1992] and "623 websites" in yintro[1993] and "2,738 websites" in yintro[1994] and "more than 10,000 websites" in yintro[1994]
L.to_pickle(f"{WORK}/list.pkl")

# ---------------- History of the World Wide Web: facts quoted ----------------
HT = wtext(WP[HIST_TITLE]["html"])
for s in ("was published on 20 December 1990", "In January 1991, the first web servers outside CERN were switched on",
          "On 6 August 1991, Berners-Lee published a short summary of the World Wide Web project on the newsgroup alt.hypertext",
          "This was the first web server outside of Europe and the first in North America", "on 30 April 1993, CERN announced that the World Wide Web would be free to anyone",
          "Paul Kunz from the Stanford Linear Accelerator Center (SLAC) visited CERN in September 1991", "NeXT Computer was used by Berners-Lee as the web server",
          "Mosaic was an immediate hit", "published a more formal proposal on 12 November 1990"):
    assert s in HT, s

# ---------------- 2. Wikidata websites ----------------
D = pd.read_csv(f"{RAW}/wd_websites.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
D.columns = [c.lstrip("?") for c in D.columns]
chk["wd_rows"] = len(D)
qid = lambda s: s.str.extract(r"(Q\d+)>?$")[0]
D["Q"] = qid(D.w); D["coQ"] = qid(D.co); D["hqQ"] = qid(D.hq)
D["label"] = D.wLabel.str.replace(r'^"(.*)"@\w+$', r"\1", regex=True).map(lambda s: s.encode().decode("unicode_escape").encode("latin-1").decode("utf-8") if "\\u" in s else s)
D["y"] = pd.to_numeric(D.inc.str[:4], errors="coerce"); D["date"] = D.inc.str[:10]
D["url_"] = D.url.str.strip("<>"); D["en_"] = D.en.str.strip("<>")
xy = D.hqc.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)")
D["hlon"] = pd.to_numeric(xy[0]); D["hlat"] = pd.to_numeric(xy[1])
assert D.y.notna().all()
chk["wd_items"] = int(D.Q.nunique())
chk["wd_multi_inception"] = int((D.groupby("Q").date.nunique() > 1).sum()); chk["wd_multi_country"] = int((D.groupby("Q").coQ.nunique() > 1).sum())
D["co_iso"] = D.coQ.map(Q2ISO)
chk["wd_country_unmatched"] = sorted(set(D.coQ.dropna()) - set(Q2ISO))
D["hq_iso"] = [pip(lo, la) if not np.isnan(la) else None for lo, la in zip(D.hlon, D.hlat)]
out, disagree = [], []
for q, g in D.groupby("Q", sort=False):
    g0 = g.sort_values("date")
    hq = g[g.hlat.notna()]
    cos = [c for c in g.co_iso.dropna().unique()]
    hq_isos = [c for c in hq.hq_iso.dropna().unique()]
    # the headquarters point is the more specific record: where Wikidata's country disagrees with it (a legal domicile
    # such as the Cayman Islands, or an error), the point wins
    if hq_isos:
        co = next((c for c in cos if c in hq_isos), hq_isos[0]); co_src = "P17" if co in cos else "HQ"
        if cos and co not in cos: disagree.append((q, g0.label.iloc[0], cos, co))
    else:
        co = cos[0] if cos else None; co_src = "P17" if co else None
    hr = hq[hq.hq_iso == co].iloc[0] if co and len(hq[hq.hq_iso == co]) else (hq.iloc[0] if len(hq) else None)
    urls = [u for u in g.url_.unique() if u]
    out.append({"Q": q, "label": g0.label.iloc[0], "date": g0.date.iloc[0], "y": int(g0.y.iloc[0]), "iso": co, "co_src": co_src,
                "lat": float(hr.hlat) if hr is not None else np.nan, "lon": float(hr.hlon) if hr is not None else np.nan,
                "url": urls[0] if urls else "", "en": next((e for e in g.en_.unique() if e), ""), "n_countries": len(cos)})
W = pd.DataFrame(out)
chk["wd_country_hq_override"] = len(disagree); chk["wd_country_hq_override_examples"] = [d[1] for d in disagree[:12]]
W["newsgroup"] = W.label.str.match(NEWSGROUP).astype(int)
REG = lambda i: None if not isinstance(i, str) else "United States" if i == "USA" else "Europe" if CONT.get(i) == "Europe" else "Rest of the world"
W["region"] = W.iso.map(REG)
# sensitivity check only: the country of the site's own country code domain (.pl, .de...), for items Wikidata gives no
# country; generic-looking codes often used for other purposes (.tv, .fm, .io...) are skipped
A2u = dict(A2ISO); A2u["uk"] = A2u.get("gb", "GBR")
GENERIC = {"tv", "fm", "io", "cc", "ws", "me", "co", "ag", "am", "nu", "to", "ly", "la", "md", "ai", "gg", "vg", "tk", "su", "eu"}
def url_iso(u):
    m = re.match(r"https?://([^/:]+)", u or "")
    if not m: return None
    tld = m.group(1).lower().rstrip(".").rsplit(".", 1)[-1]
    return None if tld in GENERIC else A2u.get(tld)
W["url_iso"] = W.url.map(url_iso)
W["iso_plus"] = W.iso.where(W.iso.notna(), W.url_iso)
W["region_plus"] = W.iso_plus.map(REG)
W["cont"] = W.iso.map(CONT)
chk["wd_newsgroups"] = W[W.newsgroup == 1].label.tolist()
W.to_pickle(f"{WORK}/wd.pkl")

# ---------------- 3. ccTLDs ----------------
C = pd.read_csv(f"{RAW}/wd_cctld.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
C.columns = [c.lstrip("?") for c in C.columns]
C["tld"] = C.tLabel.str.replace(r'^"(.*)"@\w+$', r"\1", regex=True)
C["coQ"] = qid(C.co); C["country_label"] = C.coLabel.str.replace(r'^"(.*)"@\w+$', r"\1", regex=True)
C["date"] = C.inc.str[:10]; C["y"] = pd.to_numeric(C.inc.str[:4], errors="coerce")
chk["cc_rows"] = len(C); chk["cc_items"] = int(C.t.nunique()); chk["cc_with_date"] = int(C.drop_duplicates("t").y.notna().sum())
asc = C[C.tld.str.fullmatch(r"\.[a-z]{2}")].copy()
asc["a2"] = asc.tld.str[1:]
A2 = dict(A2ISO); A2["uk"] = A2.pop("gb", "GBR")
asc["iso"] = asc.a2.map(A2)
asc["co_iso"] = asc.coQ.map(Q2ISO)
# Wikipedia ccTLD table: Year registered column
th = WP[CC_TITLE]["html"]
tb = re.sub(r"<style.*?</style>|<sup.*?</sup>", "", re.findall(r'<table class="wikitable.*?</table>', th, flags=re.S)[0], flags=re.S)
wy = {}
for tr in re.findall(r"<tr.*?</tr>", tb, flags=re.S):
    cells = [wtext(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S)]
    if len(cells) > 3 and re.fullmatch(r"\.[a-z]{2}", cells[0]):
        wy[cells[0]] = cells[3]
chk["cc_wiki_rows"] = len(wy); chk["cc_wiki_with_year"] = sum(1 for v in wy.values() if v)
asc["wiki_year"] = asc.tld.map(wy).fillna("")
cc = (asc[asc.iso.notna()].sort_values("date", na_position="last").drop_duplicates("iso"))
cc = cc[["tld", "iso", "date", "y", "wiki_year", "country_label", "co_iso"]].reset_index(drop=True)
# agreement between Wikidata's inception year and Wikipedia's year column where both exist
both = cc[(cc.wiki_year.str.fullmatch(r"\d{4}")) & cc.y.notna()]
chk["cc_both"] = len(both); chk["cc_agree"] = int((both.wiki_year.astype(int) == both.y.astype(int)).sum())
chk["cc_disagree"] = both[both.wiki_year.astype(int) != both.y.astype(int)][["tld", "y", "wiki_year"]].values.tolist()
cc.to_pickle(f"{WORK}/cctld.pkl")
pred = C[C.tld.isin(set(PRED.values()))].sort_values("date").drop_duplicates("tld")
chk["cc_pred"] = {r.tld: r.date for r in pred.itertuples()}
assert set(chk["cc_pred"]) == set(PRED.values())
# list of Internet TLDs: only used to confirm the ccTLD count of the period
LT = wtext(WP[TLD_TITLE]["html"])
jsave({"names": NAME, "cont": CONT}, f"{WORK}/nemeta.json")
jsave(chk, f"{WORK}/checks.json", indent=1)
print("list", len(L), "unique", chk["list_unique"], "| wikidata items", len(W), "1990 to 2000:", int(((W.y >= 1990) & (W.newsgroup == 0)).sum()),
      "| ccTLDs matched", len(cc), "with date", int(cc.y.notna().sum()), "| cc agree", chk["cc_agree"], "/", chk["cc_both"], chk["cc_disagree"])
print("unmatched Wikidata countries", chk["wd_country_unmatched"], "newsgroups", chk["wd_newsgroups"])
