## Title

[OC] How the web spread: from one server at CERN in December 1990 to 83 countries with a recorded website by 2000. 70% of the early sites in Wikipedia's pre-1995 list that can be placed were American

## Body

I coded every entry in Wikipedia's "List of websites founded before 1995" (119 sites) and added 2,208 websites with a founding date in Wikidata, plus the date each country got its own internet domain. In 1991 and 1992, 12 of the 17 listed sites were physics labs, universities or libraries (CERN, SLAC, Nikhef, KEK); by 1994 it was 3 of 74, and the biggest group was fan and hobby pages. The list is 70% American among sites I could place, but Wikidata's websites of the decade are only 28% American and 48% European: the English-language list remembers the American web. Caveats: "first recorded" means first in these sources, not the true first; Wikidata founding dates before 1993 are mostly the founding of the organisation behind a site, so I only use Wikidata from 1993 for country firsts. Interactive map with a play button, every site clickable: https://maps.tristanhotham.com/first-websites/

## Source comment

Sources: Wikipedia, "List of websites founded before 1995" (my coding of country, kind and status) and "History of the World Wide Web" (CC BY-SA 4.0); Wikidata websites with an inception (P571) and country code top-level domains (CC0); Natural Earth outlines.

Tools: Python (pandas, shapely, pyproj, matplotlib); MapLibre for the interactive map.

Interactive version: https://maps.tristanhotham.com/first-websites/
Paper: https://doi.org/10.5281/zenodo.23878602
Blog post: https://blog.tristanhotham.com/2026/10/31/first-websites/
