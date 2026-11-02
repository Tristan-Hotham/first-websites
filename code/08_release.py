"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23878602, https://doi.org/10.5281/zenodo.23878602 and https://blog.tristanhotham.com/2026/10/31/first-websites/ stay as placeholders for the publisher. Needs only data/ (not raw/)."""
import json as _json, shutil, zipfile, importlib.util
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_First_Websites"
L, WD, F, CC = R["list"], R["wd"], R["firsts"], R["cctld"]

# the page build checks the shared facts; these are numbers written in words or alt text in the blog and collage
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "04_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
assert [c["n"] for c in L["countries"]] == [74, 11, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1] and L["no_country"] == 13
TS = L["type_status"]
assert (TS["Fans, hobbies and fun"]["live"], TS["Fans, hobbies and fun"]["gone"], TS["Fans, hobbies and fun"]["unstated"]) == (11, 5, 10)
assert TS["News, magazines and broadcasters"]["live"] == 8 and TS["Government and politics"]["gone"] == 0 and TS["Search engines and directories"]["gone"] == 3
assert [L["types"][t] for t in TN] == [15, 8, 20, 16, 10, 10, 14, 26]
Y = {d["y"]: d for d in WD["years"]}
assert [Y[y]["n"] for y in (1990, 1991, 1992, 1993)] == [51, 45, 43, 60] and (Y[1994]["n"], Y[1995]["n"], Y[1999]["n"], Y[2000]["n"]) == (104, 191, 438, 437)
eu = [Y[y]["Europe_pct"] for y in Y]; us = [Y[y]["United States_pct"] for y in Y]; rw = [Y[y]["Rest of the world_pct"] for y in Y]
assert 32.5 < min(eu) and max(eu) < 58.5 and 12.5 < min(us) and max(us) < 46.5 and 14 < min(rw) and max(rw) < 41.5
assert sum(Y[y]["Europe"] > max(Y[y]["United States"], Y[y]["Rest of the world"]) for y in Y) >= 6        # "in most years"
assert round(L["us_share_by_year"]["1991"]) == 33 and round(L["us_share_by_year"]["1994"]) == 78
assert (CC["cum"]["1985"], CC["cum"]["1990"], CC["cum"]["1994"], CC["cum"]["2000"]) == (3, 46, 130, 223)
assert (F["cum_by_year"]["1990"], F["cum_by_year"]["1992"], F["cum_by_year"]["1994"], F["cum_by_year"]["2000"]) == (1, 7, 35, 83)
B = F["by_iso"]
assert all(B[i]["y"] == 1993 for i in ("CAN", "RUS", "ARG", "AUS", "DEU", "ITA", "ESP", "FIN")) and all(B[i]["y"] == 1995 for i in ("BRA", "CHN", "ZAF"))
assert all(B[i]["y"] <= 1992 for i in ("CHE", "USA", "NLD", "IRL", "ISR", "JPN", "FRA"))

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{[^|}]+\}\}", post)) <= {"https://doi.org/10.5281/zenodo.23878602"}
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "The first websites: how the web spread around the world",
        "slug": "first-websites",
        "excerpt": f"From one server at CERN in December 1990 to {F['n']} countries with a recorded website by 2000. I coded Wikipedia's list of {L['n']} websites founded before 1995 and added {WD['n']:,} more from Wikidata: the web began with physicists and was soon overwhelmingly American, at least in the English-language memory of it.",
        "seo_description": f"How the World Wide Web spread from CERN in 1990 to {F['n']} countries by 2000: the first websites, mapped from Wikipedia and Wikidata.",
        "tags": ["internet history", "World Wide Web", "maps", "data visualisation", "CERN", "Wikipedia", "Wikidata", "1990s"],
        "header_alt": f"Title card reading 'The first websites' in black, blue and purple under a mock browser address bar showing http://info.cern.ch/, beside a world map with countries coloured from dark blue (1990) to pale gold (2000) by the year of their earliest recorded website, the United States and western Europe darkest, much of Africa grey. Text: from one server at CERN to {F['n']} countries; {L['us_pct_known']:.0f}% of the early sites in Wikipedia's list with a known country were American."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/first-websites_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"first-websites/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"first-websites/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "first-websites/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "\"").replace("''", "\"")
zmeta = {"title": "The First Websites: How the World Wide Web Spread Around the World, 1990 to 2000",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p><p>Sources: Wikipedia (CC BY-SA 4.0), Wikidata (CC0), Natural Earth (public domain).</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["World Wide Web", "internet history", "early websites", "diffusion", "country code top-level domains", "Wikipedia", "Wikidata", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://en.wikipedia.org/wiki/List_of_websites_founded_before_1995", "relation": "isDerivedFrom", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
