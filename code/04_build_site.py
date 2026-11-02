"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, world.json, cities) is embedded. Facts stated in words are checked
here. The full-screen map snippet (code/fullscreen_snippet.html) is pasted before </body>. 10.5281/zenodo.23878602 and https://blog.tristanhotham.com/2026/10/31/first-websites/ stay
as placeholders for the publisher. Needs only data/ (not raw/)."""
import json
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
L, WD, F, CC, E = R["list"], R["wd"], R["firsts"], R["cctld"], R["entries"]

# facts stated in words (page, blog, paper, collage)
assert L["by_year"] == {"1991": 3, "1992": 14, "1993": 28, "1994": 74} and L["n"] == 119 and L["rows"] == 120
assert L["sci_uni_9192"] == 12 and L["n_9192"] == 17                                   # laboratories, universities, libraries in 1991 and 1992
assert L["top_type"] == "Fans, hobbies and fun" and L["fun_94"] == max(L["year_type"]["1994"].values())
assert L["countries"][0]["iso"] == "USA" and L["countries"][1]["iso"] == "GBR" and L["countries"][2]["iso"] == "IRL"
assert sorted(c["iso"] for c in L["countries"] if c["iso"] != "USA" and SITE["cn"][c["iso"]][4] != "Europe") == ["CAN", "ISR", "JPN", "MEX"]
assert all(v > 50 for k, v in L["us_share_by_year"].items() if k != "1991")           # "a majority from 1992 on"
assert 66 < L["us_pct_known"] < 75                                                    # "about seven in ten"
assert F["cum_by_year"]["1992"] == 7 and {r["iso"] for r in F["rows"] if r["y"] <= 1992} == {"CHE", "USA", "NLD", "IRL", "ISR", "JPN", "FRA"}
assert all(r["src"] == "list" for r in F["rows"] if r["y"] <= 1992)
assert F["by_iso"]["CHE"]["y"] == 1990 and F["by_iso"]["USA"]["name"] == "Stanford Linear Accelerator Center"
assert [w["iso"] for w in WD["top"][:5]] == ["USA", "RUS", "GBR", "DEU", "FRA"]
assert WD["early"] > 2 * 60                                                            # "more than twice the fifty to sixty"
assert WD["us_pct"] < 33 and WD["europe_pct"] > 45                                     # "under a third", "almost half"
assert CC["gap_list_min"] == -1 and [r["country"] for r in F["rows"] if r["src"] == "list" and r["iso"] == "LUX"] == ["Luxembourg"]
assert CC["first"] == ".us" and CC["us_month"] == "February 1985"
assert E["slac"]["when"] == "12 December 1991" and E["imdb"]["when"] == "late 1993" and E["tech"]["when"] == "May 1993"
assert E["coffee"]["when"] == "November 1993" and E["jumpstation"]["when"] == "12 December 1993" and E["kek"]["when"] == "September 1992"
assert E["nikhef"]["when"] == "February 1992" and E["curia"]["when"] == E["huji"]["when"] == "April 1992"
assert {r["cont"] for r in F["rows"]} == {"Europe", "North America", "Asia", "South America", "Africa", "Oceania"}   # "every inhabited continent"
assert L["live"] + L["gone"] + L["unstated"] == L["n"]


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R)
    left = re.findall(r"\{\{[^}]*\}\}", html)
    assert set(left) <= {"10.5281/zenodo.23878602", "https://blog.tristanhotham.com/2026/10/31/first-websites/"}, left[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([c for c in jload(f"{DATA}/cities.json") if c["pop"] >= 4e5]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
