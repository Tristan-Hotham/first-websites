"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json. Needs only data/."""
from common import *

R = jload(f"{DATA}/results.json")
L, WD, F, CC = R["list"], R["wd"], R["firsts"], R["cctld"]
N = lambda v: f"{round(v):,}"
readme = f"""# The first websites: how the World Wide Web spread around the world, 1990 to 2000

From info.cern.ch, published at CERN on 20 December 1990, through SLAC in California (the first web server outside Europe, December 1991), to the earliest recorded website in each country and the creation of every country code internet domain. Built from Wikipedia's "List of websites founded before 1995" (coded entry by entry), {N(WD['n'])} websites with a founding date in Wikidata, and Wikidata's dates for country code top-level domains.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- The pre-1995 list holds {L['n']} distinct websites: {L['by_year']['1991']} from 1991, {L['by_year']['1992']} from 1992, {L['by_year']['1993']} from 1993, {L['by_year']['1994']} from 1994. In 1991 and 1992, {L['sci_uni_9192']} of {L['n_9192']} were laboratories, universities or libraries; in 1994, {L['sci_uni_94']} of {L['n_94']}. Fans, hobbies and fun is the largest kind ({L['types']['Fans, hobbies and fun']}).
- Where: {L['n_countries']} countries. Of the {L['known']} websites that can be placed, {L['us']} ({L['us_pct_known']:.0f}%) were American, {L['europe']} ({L['europe_pct_known']:.0f}%) European and {L['rest']} elsewhere (Canada, Japan, Israel, Mexico). {L['no_country']} cannot be placed.
- Today: the list's own text says {L['live']} are still online and {L['gone']} have closed; for {L['unstated']} it does not say.
- Wikidata: {N(WD['items'])} websites with an inception up to 2000; {N(WD['pre1990'])} are dated before 1990 (the founding of the organisation, not a web launch) and are left out, leaving {N(WD['n'])} from 1990 to 2000, peaking at {WD['peak_n']} in {WD['peak_year']}. Only {WD['country_pct']:.0f}% have a country. Of those with one, {WD['us_pct']:.0f}% are American and {WD['europe_pct']:.0f}% European: the reverse of the list. Wikidata dates {WD['early']} websites to 1990 to 1992, more than twice the fifty to sixty that existed at the end of 1992, so those dates are mostly organisations' founding years.
- Countries: with the list and Wikidata (from 1993), {F['cum_by_year']['1992']} countries had a recorded website by the end of 1992, {F['cum_by_year']['1994']} by 1994 and {F['n']} by 2000. {F['n_doubt']} Wikidata firsts are dated before the country had its own domain and are flagged. This is the earliest recorded in these sources, not the true first.
- Domains: {CC['by1990']} country code domains existed by the end of 1990 and {CC['by2000']} by 2000 (Wikidata dates). For the {CC['gap_list_n']} countries in the list, the first recorded website came a median of {CC['gap_list_median']:.0f} years after the domain.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; all page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/pre1995_list.csv` | The {L['rows']} entries of Wikipedia's list ({L['n']} counted): year section, date in the text, my coding of kind, country, place (with the basis for it) and coordinates, status stated in the text, host names written in the text, links to the article and the list entry. |
| `data/wikidata_websites_1990_2000.csv` | The {N(WD['n'])} Wikidata websites with an inception from 1990 to 2000: id, label, inception, country and where it comes from, region, headquarters coordinates, official address, English Wikipedia article. |
| `data/wikidata_inception_before_1990.csv` | The {N(WD['pre1990'])} items left out because their inception predates the web. |
| `data/first_website_by_country.csv` | The earliest recorded website in each of {F['n']} countries, its source, and the country's domain year. |
| `data/cctld_delegation.csv` | Two-letter country code domains matched to countries, with Wikidata's date and Wikipedia's year. |
| `data/websites_by_year.csv` | Per year: Wikidata websites by region, the list, new countries, countries reached, domains. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json`, `data/world.json`, `data/countries.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- The list is prose, one paragraph per website under a heading per year. I split it on the headings; Chabad.org appears under 1993 and 1994 and is counted once. Year = the section. CERN is dated 20 December 1990 on the map, from "History of the World Wide Web" (the list puts it in 1991).
- Country and place: named in the text for {L['basis']['text']} entries; otherwise the organisation's well-known home ({L['basis']['org']}), or country only ({L['basis']['country']}); {L['basis']['none']} unknown. Each point is checked against its country outline. Kind: one of eight, my coding. Status: only what the text says, each backed by a phrase checked in code.
- Wikidata: one row per item, earliest inception; country from the headquarters coordinates where present, else Wikidata's country. Inception before 1990 = the parent organisation's founding; dropped. Usenet newsgroups dropped. Region: United States, Europe (Natural Earth continent, incl. Russia), rest of the world.
- Earliest recorded website per country: earliest of the list and Wikidata inceptions from 1993 on. Flag (not filter): a Wikidata first dated before the country's own domain (predecessors .su, .yu, .cs, .an counted).
- Domains: Wikidata inception of the two-letter ccTLD, matched by code (.uk for the United Kingdom).

## How to rerun

Needs Python 3 with numpy, pandas, shapely, pyproj, matplotlib and fontTools, xelatex and pdftotext; node with Playwright for `code/qa.js`. Steps 01 to 03 read `raw/` (Wikidata TSVs and Wikipedia parse HTML, not published) and Natural Earth in `/home/claude/newdata/raw/geo/`; steps 04 onward need only `data/`. Intermediate files go to `/dev/shm/firstwebsites/work` (set `FWTMP` to change).

```
python3 code/01_clean.py        # split and code the list; clean Wikidata websites and ccTLDs
python3 code/02_geo.py          # outlines, country names, cities
python3 code/03_results.py      # results.json, data tables, page data
python3 code/04_build_site.py   # index.html
python3 code/05_figures.py      # header, blog and paper figures
python3 code/06_paper.py        # paper PDF
python3 reddit/collage.py       # collage
python3 code/07_readme.py       # README, LICENSE, Reddit post
python3 code/08_release.py      # blog post, Zenodo files
```

## Sources and licences

- Wikipedia: "List of websites founded before 1995", "History of the World Wide Web", "Country code top-level domain", "List of Internet top-level domains" (revision ids in `data/results.json`). CC BY-SA 4.0. Facts are taken from them; no article text is reproduced.
- Wikidata: websites (Q35127 and subclasses) and country code top-level domains (Q42032), via QLever. CC0.
- Natural Earth countries and populated places (https://www.naturalearthdata.com/). Public domain.

## Citation

Hotham, T. (2026) The first websites: how the World Wide Web spread around the world, 1990 to 2000. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)

lic = open("/home/claude/studies/rocket-launches/LICENSE", encoding="utf-8").read().split("\n\n\nThis licence covers")[0]
lic += """


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post, the figures and the derived data
files in data/ are released under CC BY 4.0. The coding of Wikipedia's "List
of websites founded before 1995" is derived from Wikipedia (CC BY-SA 4.0);
data/pre1995_list.csv is therefore also shared under CC BY-SA 4.0. Wikidata
is CC0. Natural Earth is public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)

post = f"""## Title

[OC] How the web spread: from one server at CERN in December 1990 to {F['n']} countries with a recorded website by 2000. {L['us_pct_known']:.0f}% of the early sites in Wikipedia's pre-1995 list that can be placed were American

## Body

I coded every entry in Wikipedia's "List of websites founded before 1995" ({L['n']} sites) and added {N(WD['n'])} websites with a founding date in Wikidata, plus the date each country got its own internet domain. In 1991 and 1992, {L['sci_uni_9192']} of the {L['n_9192']} listed sites were physics labs, universities or libraries (CERN, SLAC, Nikhef, KEK); by 1994 it was {L['sci_uni_94']} of {L['n_94']}, and the biggest group was fan and hobby pages. The list is {L['us_pct_known']:.0f}% American among sites I could place, but Wikidata's websites of the decade are only {WD['us_pct']:.0f}% American and {WD['europe_pct']:.0f}% European: the English-language list remembers the American web. Caveats: "first recorded" means first in these sources, not the true first; Wikidata founding dates before 1993 are mostly the founding of the organisation behind a site, so I only use Wikidata from 1993 for country firsts. Interactive map with a play button, every site clickable: {PAGE}

## Source comment

Sources: Wikipedia, "List of websites founded before 1995" (my coding of country, kind and status) and "History of the World Wide Web" (CC BY-SA 4.0); Wikidata websites with an inception (P571) and country code top-level domains (CC0); Natural Earth outlines.

Tools: Python (pandas, shapely, pyproj, matplotlib); MapLibre for the interactive map.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
for t in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("readme, licence, post ok")
