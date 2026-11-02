# The first websites: how the World Wide Web spread around the world, 1990 to 2000

From info.cern.ch, published at CERN on 20 December 1990, through SLAC in California (the first web server outside Europe, December 1991), to the earliest recorded website in each country and the creation of every country code internet domain. Built from Wikipedia's "List of websites founded before 1995" (coded entry by entry), 2,208 websites with a founding date in Wikidata, and Wikidata's dates for country code top-level domains.

Interactive page: https://maps.tristanhotham.com/first-websites/
Paper: https://doi.org/10.5281/zenodo.23878602
Blog post: https://blog.tristanhotham.com/2026/10/31/first-websites/

## Headline results

- The pre-1995 list holds 119 distinct websites: 3 from 1991, 14 from 1992, 28 from 1993, 74 from 1994. In 1991 and 1992, 12 of 17 were laboratories, universities or libraries; in 1994, 3 of 74. Fans, hobbies and fun is the largest kind (26).
- Where: 14 countries. Of the 106 websites that can be placed, 74 (70%) were American, 25 (24%) European and 7 elsewhere (Canada, Japan, Israel, Mexico). 13 cannot be placed.
- Today: the list's own text says 43 are still online and 14 have closed; for 62 it does not say.
- Wikidata: 3,127 websites with an inception up to 2000; 915 are dated before 1990 (the founding of the organisation, not a web launch) and are left out, leaving 2,208 from 1990 to 2000, peaking at 438 in 1999. Only 59% have a country. Of those with one, 28% are American and 48% European: the reverse of the list. Wikidata dates 139 websites to 1990 to 1992, more than twice the fifty to sixty that existed at the end of 1992, so those dates are mostly organisations' founding years.
- Countries: with the list and Wikidata (from 1993), 7 countries had a recorded website by the end of 1992, 35 by 1994 and 83 by 2000. 5 Wikidata firsts are dated before the country had its own domain and are flagged. This is the earliest recorded in these sources, not the true first.
- Domains: 46 country code domains existed by the end of 1990 and 223 by 2000 (Wikidata dates). For the 12 countries in the list, the first recorded website came a median of 6 years after the domain.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; all page data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/pre1995_list.csv` | The 120 entries of Wikipedia's list (119 counted): year section, date in the text, my coding of kind, country, place (with the basis for it) and coordinates, status stated in the text, host names written in the text, links to the article and the list entry. |
| `data/wikidata_websites_1990_2000.csv` | The 2,208 Wikidata websites with an inception from 1990 to 2000: id, label, inception, country and where it comes from, region, headquarters coordinates, official address, English Wikipedia article. |
| `data/wikidata_inception_before_1990.csv` | The 915 items left out because their inception predates the web. |
| `data/first_website_by_country.csv` | The earliest recorded website in each of 83 countries, its source, and the country's domain year. |
| `data/cctld_delegation.csv` | Two-letter country code domains matched to countries, with Wikidata's date and Wikipedia's year. |
| `data/websites_by_year.csv` | Per year: Wikidata websites by region, the list, new countries, countries reached, domains. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json`, `data/world.json`, `data/countries.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- The list is prose, one paragraph per website under a heading per year. I split it on the headings; Chabad.org appears under 1993 and 1994 and is counted once. Year = the section. CERN is dated 20 December 1990 on the map, from "History of the World Wide Web" (the list puts it in 1991).
- Country and place: named in the text for 42 entries; otherwise the organisation's well-known home (49), or country only (15); 13 unknown. Each point is checked against its country outline. Kind: one of eight, my coding. Status: only what the text says, each backed by a phrase checked in code.
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

Hotham, T. (2026) The first websites: how the World Wide Web spread around the world, 1990 to 2000. Zenodo. https://doi.org/10.5281/zenodo.23878602

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
