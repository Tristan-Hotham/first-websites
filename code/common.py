"""Shared paths, groupings, the hand curation of the pre-1995 list, and helpers for the first-websites project.

Raw inputs (read by 01_clean.py and 02_geo.py only; raw/ is not needed once data/ is built):
  raw/wd_websites.tsv   Wikidata (CC0), queried through QLever: every item that is an instance of website (Q35127) or a
      subclass, with an inception (P571) up to 2000, its country (P17), headquarters location (P159) and that place's
      coordinates (P625), official website (P856) and English Wikipedia article. One row per combination of values, so an
      item with two URLs or two countries appears more than once.
  raw/wd_cctld.tsv      Wikidata (CC0): country code top-level domains (instances of Q42032) with inception where known
      and country.
  raw/wiki_pages.json   English Wikipedia (CC BY-SA 4.0), parse HTML with revision ids: "List of websites founded before
      1995", "History of the World Wide Web", "List of Internet top-level domains", "Country code top-level domain".
  /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson, ne_50m_land.geojson, ne_10m_populated_places_simple.geojson
      Natural Earth, public domain.

The core source is the Wikipedia list. It is written as prose, one short section per website under a heading for each
year (1991 to 1994), not as a table. 01_clean.py splits it into entries; the country, place, type and status of each entry
are my reading of its text, set out in LIST below, with a note of where the place comes from.
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("FW_RAW", os.path.join(ROOT, "raw"))
GEO = os.environ.get("FW_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("FW_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("FWTMP", "/dev/shm/firstwebsites"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "first-websites"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23878602"                 # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/first-websites/"           # filled in by the publisher
FETCHED = "2026"                # sources fetched in 2026; year only in public copy
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
Y0, Y1 = 1990, 2000             # the study window
WEB_FLOOR = 1990                # a Wikidata inception before this cannot be a web launch: it dates the parent organisation
STRICT_FLOOR = 1993             # for "first recorded website in a country" a Wikidata inception counts from this year (see 03)

LIST_TITLE = "List of websites founded before 1995"
HIST_TITLE = "History of the World Wide Web"
TLD_TITLE = "List of Internet top-level domains"
CC_TITLE = "Country code top-level domain"

# Kinds of website, for the pre-1995 list. Order = legend and stack order.
TYPES = [("Science and research", "#2F5FA7"), ("Universities and libraries", "#7FA7D9"), ("Companies and shops", "#C8322B"),
         ("News, magazines and broadcasters", "#E0A11B"), ("Government and politics", "#2E9A8C"), ("Search engines and directories", "#7B57A8"),
         ("Culture, causes and faith", "#D46A8C"), ("Fans, hobbies and fun", "#8C8478")]
TN = [t for t, _ in TYPES]; TCOL = dict(TYPES)
TK = {"sci": TN[0], "uni": TN[1], "com": TN[2], "news": TN[3], "gov": TN[4], "dir": TN[5], "cul": TN[6], "fun": TN[7]}

# year colours for maps (1990 to 2000), dark blue to gold, spaced so the busy early years stand apart
YCOL = ["#0B1F6B", "#1F48C9", "#4F86E8", "#7B5CC4", "#B04FA8", "#D9577E", "#EB6F5A", "#F28C45", "#F5A93B", "#F2C14E", "#E9DA84"]

# Regions for the geography shares
REGIONS = [("United States", "#2F5FA7"), ("Europe", "#7B57A8"), ("Rest of the world", "#E0A11B")]
RN = [r for r, _ in REGIONS]; RCOL = dict(REGIONS)

# Places used for the list, with coordinates (decimal degrees, to about a kilometre; for a laboratory or campus, the site).
PLACES = {
    "CERN, Meyrin": (46.234, 6.055), "SLAC, Menlo Park": (37.418, -122.205), "Amsterdam": (52.356, 4.951), "Urbana": (40.110, -88.228),
    "Batavia": (41.840, -88.257), "Chapel Hill": (35.910, -79.050), "Dayton": (39.781, -84.064), "Columbus": (40.002, -83.015),
    "Villeurbanne, Lyon": (45.782, 4.866), "Cork": (51.893, -8.492), "Jerusalem": (31.776, 35.198), "San Francisco": (37.775, -122.419),
    "Houston": (29.760, -95.370), "Tsukuba": (36.149, 140.076), "Palo Alto": (37.402, -122.149), "New York": (40.713, -74.006),
    "Brooklyn, New York": (40.669, -73.942), "Paris": (48.857, 2.352), "Clamart": (48.800, 2.266), "Cambridge, Massachusetts": (42.360, -71.094),
    "Westford": (42.623, -71.488), "Cardiff": (51.487, -3.179), "Santa Cruz": (36.997, -122.060), "Dublin": (53.344, -6.267),
    "Trondheim": (63.419, 10.402), "Stirling": (56.146, -3.920), "Los Alamos": (35.881, -106.298), "Washington": (38.897, -77.036),
    "Nottingham": (52.954, -1.158), "Tokyo": (35.681, 139.767), "Brussels": (50.822, 4.395), "Cambridge": (52.211, 0.092),
    "Hartford": (41.747, -72.690), "Chicago": (41.878, -87.630), "Ottawa": (45.421, -75.697), "Cupertino": (37.332, -122.030),
    "Mountain View": (37.386, -122.084), "Edmonton": (53.523, -113.526), "London": (51.507, -0.128), "Birmingham": (52.450, -1.930),
    "Calgary": (51.045, -114.072), "Luxembourg": (49.612, 6.130), "Minneapolis": (44.978, -93.265), "Austin": (30.286, -97.739),
    "Richmond": (37.539, -77.434), "Swarthmore": (39.906, -75.354), "Pittsburgh": (40.443, -79.943), "Los Angeles": (34.052, -118.244),
    "Redmond": (47.674, -122.121), "Boston": (42.360, -71.059), "Raleigh": (35.780, -78.639), "Tucson": (32.232, -110.951),
    "Providence": (41.827, -71.403), "Portland": (45.523, -122.681), "Martin": (36.343, -88.865), "Prague": (50.075, 14.437),
    "Seattle": (47.655, -122.304), "Boulder": (40.007, -105.266), "Armonk": (41.126, -73.714), "Geneva": (46.204, 6.143),
}

# The pre-1995 list, entry by entry, in the order of the article (number = order in the article).
# Fields: n, country (ISO3, or None where the text and the organisation give no country), place (key of PLACES or None),
# basis of the place ('text': named in the list's text; 'org': not in the text, the organisation's well-known home;
# 'country': only the country is known, nothing plotted), type key (TK), status from the text ('live': the text says it is
# still online, at the same or a new address; 'gone': the text says it closed, went offline or was absorbed; '': not stated).
LIST = [
    (1, "CHE", "CERN, Meyrin", "text", "sci", ""), (2, "CHE", "CERN, Meyrin", "text", "dir", ""), (3, "USA", "SLAC, Menlo Park", "text", "sci", ""),
    (4, "NLD", "Amsterdam", "org", "sci", ""), (5, "USA", "Urbana", "org", "sci", ""), (6, "USA", "Batavia", "text", "sci", ""),
    (7, "USA", "Chapel Hill", "text", "uni", ""), (8, "USA", "Dayton", "org", "uni", ""), (9, "USA", "Columbus", "org", "uni", ""),
    (10, "FRA", "Villeurbanne, Lyon", "org", "sci", ""), (11, "IRL", "Cork", "text", "uni", "live"), (12, "ISR", "Jerusalem", "text", "uni", ""),
    (13, "USA", "San Francisco", "text", "cul", ""), (14, None, None, "", "com", "gone"), (15, "USA", "Houston", "text", "com", "live"),
    (16, "JPN", "Tsukuba", "org", "sci", "live"), (17, "USA", "Palo Alto", "text", "fun", "live"),
    # 1993
    (18, "USA", "New York", "org", "news", ""), (19, "USA", "Brooklyn, New York", "org", "cul", ""), (20, "USA", "Chapel Hill", "org", "fun", ""),
    (21, "FRA", "Clamart", "org", "com", ""), (22, "USA", "Cambridge, Massachusetts", "text", "dir", ""), (23, "USA", "Westford", "org", "sci", "live"),
    (24, "GBR", "Cardiff", "text", "fun", ""), (25, "USA", "Santa Cruz", "text", "cul", ""), (26, "IRL", "Dublin", "org", "com", ""),
    (27, "NOR", "Trondheim", "text", "fun", ""), (28, "GBR", "Stirling", "text", "dir", "gone"), (29, "USA", "Los Alamos", "text", "sci", "live"),
    (30, None, None, "", "fun", ""), (31, "USA", "Chapel Hill", "text", "cul", "live"), (32, "USA", "Cambridge, Massachusetts", "text", "news", ""),
    (33, "USA", "Washington", "org", "gov", ""), (34, "GBR", "Nottingham", "org", "com", ""), (35, "USA", "New York", "org", "news", "live"),
    (36, "JPN", "Tokyo", "org", "com", "live"), (37, "USA", "Palo Alto", "org", "sci", ""), (38, "USA", "Palo Alto", "org", "sci", "gone"),
    (39, "USA", "Cambridge, Massachusetts", "org", "fun", ""), (40, "BEL", "Brussels", "org", "sci", ""), (41, "IRL", "Dublin", "text", "uni", ""),
    (42, "CHE", "Geneva", "org", "sci", "live"), (43, "GBR", "Cambridge", "org", "uni", ""), (44, "USA", "Hartford", "text", "news", "gone"),
    (45, "USA", "San Francisco", "org", "news", "live"),
    # 1994
    (46, "GBR", "Nottingham", "org", "dir", "gone"), (47, "USA", None, "country", "com", ""), (48, "USA", "Chicago", "org", "cul", "live"),
    (49, "CAN", "Ottawa", "org", "cul", "live"), (50, "USA", "Cupertino", "org", "com", ""), (51, "USA", "San Francisco", "text", "cul", ""),
    (52, "USA", None, "country", "cul", ""), (53, "USA", "Mountain View", "org", "fun", "gone"), (54, "USA", None, "country", "fun", "live"),
    (55, "CAN", "Edmonton", "text", "fun", "live"), (56, "GBR", "London", "org", "news", "live"), (57, "USA", None, "country", "fun", ""),
    (58, "GBR", "Birmingham", "text", "gov", "live"), (59, "USA", "Chicago", "org", "news", "live"), (60, None, None, "", "cul", ""),
    (61, "CAN", "Calgary", "org", "com", ""), (62, "USA", "Brooklyn, New York", "org", "cul", ""), (63, "USA", "San Francisco", "text", "com", "live"),
    (64, None, None, "", "cul", "live"), (65, "USA", None, "country", "dir", "gone"), (66, "USA", None, "country", "com", "gone"),
    (67, "LUX", "Luxembourg", "text", "gov", "live"), (68, "USA", "San Francisco", "org", "gov", ""), (69, "GBR", "London", "org", "news", "live"),
    (70, "USA", "Minneapolis", "org", "gov", ""), (71, "USA", "Austin", "text", "dir", "live"), (72, "USA", "San Francisco", "text", "fun", "live"),
    (73, "USA", "Columbus", "text", "fun", "gone"), (74, None, None, "", "fun", "live"), (75, "USA", None, "country", "sci", ""),
    (76, "GBR", "London", "org", "gov", "live"), (77, None, None, "", "fun", "live"), (78, "USA", "San Francisco", "org", "news", ""),
    (79, "USA", "Armonk", "org", "com", "live"), (80, None, None, "", "news", "live"), (81, "IRL", "Dublin", "org", "news", "live"),
    (82, "USA", None, "country", "com", "live"), (83, "USA", "Richmond", "text", "gov", "live"), (84, "USA", "Swarthmore", "org", "fun", "live"),
    (85, "USA", "New York", "org", "cul", "live"), (86, "USA", "Pittsburgh", "text", "dir", "live"), (87, "USA", "Los Angeles", "org", "cul", ""),
    (88, "USA", "Redmond", "org", "com", ""), (89, "USA", "Boston", "text", "cul", ""), (90, "USA", None, "country", "fun", "live"),
    (91, "USA", "Raleigh", "text", "news", ""), (92, None, None, "", "fun", "live"), (93, "USA", "Tucson", "text", "fun", "gone"),
    (94, "USA", "New York", "org", "news", "gone"), (95, "USA", "Providence", "text", "fun", ""), (96, "USA", "Santa Cruz", "text", "com", ""),
    (97, "USA", "Portland", "org", "com", ""), (98, "USA", "Martin", "text", "uni", "live"), (99, None, None, "", "fun", "gone"),
    (100, "CZE", "Prague", "text", "news", "live"), (101, None, None, "", "fun", ""), (102, "USA", "Washington", "org", "gov", "live"),
    (103, "USA", None, "country", "sci", "live"), (104, "USA", None, "country", "com", ""), (105, "USA", None, "country", "fun", "live"),
    (106, None, None, "", "fun", "live"), (107, "USA", "San Francisco", "text", "com", ""), (108, "USA", None, "country", "fun", ""),
    (109, None, None, "", "fun", ""), (110, "GBR", "London", "org", "news", ""), (111, "USA", "Washington", "org", "gov", ""),
    (112, "USA", None, "country", "news", ""), (113, "USA", "Cambridge, Massachusetts", "text", "com", "gone"), (114, None, None, "", "fun", "gone"),
    (115, "USA", "Seattle", "text", "dir", ""), (116, "GBR", "London", "text", "com", ""), (117, "USA", "Washington", "org", "gov", ""),
    (118, "USA", "Boulder", "text", "dir", ""), (119, "USA", "Palo Alto", "org", "dir", ""), (120, "MEX", None, "country", "cul", ""),
]
LIST_DUP = {62: 19}             # Chabad.org appears under 1993 and again under 1994; counted once, in 1993
LIST_NOTES = {                  # facts about entries that the counts depend on, checked against the text in 01_clean.py
    45: "Listed under 1993, but its text says the site launched in October 1994.",
    1: "The list puts CERN's site in 1991; the History of the World Wide Web article says info.cern.ch was published on 20 December 1990.",
    120: "Placed in Mexico, the subject of the site; the list does not say where it was hosted.",
    24: "Placed at Cardiff University, which the list says first hosted it.",
    17: "Placed at Xerox PARC, which the list says hosted it.",
}
# the words in each entry's text that set its status (checked in 01_clean.py: each phrase must appear in that entry)
STATUS_EVIDENCE = {
    11: "now known as Corpus of Electronic Texts", 14: "merged with youngmonkey in 1995", 15: "still visible at www.cbss.com",
    16: "It is still online", 17: "It now resides at www.cybergrass.com", 23: "The website is still active", 28: "operated until 1994",
    29: "It is still active as arxiv.org", 31: "It remains at sito.org", 35: "The corporate website is still live", 36: "It still has a website",
    38: "It is now defunct", 42: "is still active at www.expasy.org", 44: "It went defunct in the spring of 2000", 45: "It is still live at www.wired.com",
    46: "but was short-lived", 48: "where it remains", 49: "It still operates at amnesty.ca", 53: "has since ceased operations",
    54: "This website is still active", 55: "where it is still available", 56: "It is still active at bbc.com", 58: "still functions at",
    59: "published exclusively online at www.britannica.com", 63: "still operates CitySites", 64: "It is still active at",
    65: "it was removed in February 2020", 66: "It is no longer active", 67: "It is still online at cordis.europa.eu", 69: "It is still live today",
    71: "now run by Logika Corporation", 72: "oldest still-operating webcam", 73: "until it went offline on March 7, 1998",
    74: "is still live as www.crwflags.com", 76: "It is live at www.gov.uk", 77: "It is still live at www.horror.com", 79: "It is live at www.ibm.com",
    80: "is accessible at Innerviews", 81: "irishtimes.com in 2008", 82: "It is still live at www.lawinfo.com", 83: "It remains active as lis.virginia.gov",
    84: "It is still available at www.links.net", 85: "is still active at litkicks.com", 86: "It is still live at www.lycos.com",
    90: "It is still live at nineplanets.org", 92: "It is available online at www.netboy.com", 93: "is now defunct", 94: "It operated from 1994 to April 1999",
    98: "migrated to t5k.org", 99: "It was defunct by November 2017", 100: "Still active at english.radio.cz", 102: "The site remains active",
    103: "Its current URL is yeastgenome.org", 105: "is still active", 106: "is now live at www.simpsonsarchive.com", 113: "was sold to Quick Commerce",
    114: "It is now defunct",
}

# the article each entry is about, where the heading-matched link in its paragraph is missing or points elsewhere
WIKI_FIX = {6: "Fermilab", 12: "Hebrew_University_of_Jerusalem", 24: "IMDb", 61: "Canadian_Airlines", 64: "Classical_Archives", 96: "Pizza_Hut",
            87: "Megadeth", 95: "Phish.net"}
# the launch date where the first date in the text is something else (a visit, a snapshot, a closure)
WHEN_FIX = {1: "20 December 1990", 2: "", 3: "12 December 1991", 46: "May 1994", 94: "", 95: "June 1994", 112: "June 1994",
            116: "November 1994", 65: "August 1994", 73: "1 September 1994"}

# predecessor country code domains (the state's sites used these before the present code existed)
SOVIET = ["RUS", "UKR", "BLR", "MDA", "EST", "LVA", "LTU", "GEO", "ARM", "AZE", "KAZ", "KGZ", "TJK", "TKM", "UZB"]
PRED = {**{i: ".su" for i in SOVIET}, "SRB": ".yu", "MNE": ".yu", "CUW": ".an", "CZE": ".cs", "SVK": ".cs"}

# Usenet newsgroups that Wikidata types as websites are not websites; left out of every count
NEWSGROUP = r"^(alt|rec|comp|sci|soc|talk|news|misc)\.[a-z]"
# Wikidata countries that are not Natural Earth countries: historical states map to their main successor in the window
WD_COUNTRY_FIX = {"Q29999": "NLD", "Q219060": "PSE", "Q37024": "SRB"}

iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]
NE_FIX = {"CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "PSX": "PSE", "SAH": "ESH", "KAS": "IND", "SOL": "SOM"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "word": return WORDS.get(int(v), f"{int(v):,}")
    if f == "Word": w = WORDS.get(int(v), f"{int(v):,}"); return w[0].upper() + w[1:]
    raise ValueError(f)


WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve"}


def fill(text, R, f=fmt):
    """Replace {{path|format}} tokens with numbers from R, leaving the publisher's tokens (10.5281/zenodo.23878602, https://doi.org/10.5281/zenodo.23878602, https://blog.tristanhotham.com/2026/10/31/first-websites/),
    image tokens ({{IMG|...}}) and table tokens ({{TABLE_...}}) alone."""
    return re.sub(r"\{\{(?!IMG\||DOI\}\}|DOI_URL\}\}|BLOG_URL\}\}|TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: f(get(R, m.group(1)), m.group(3)), text)


def wtext(h):
    """Plain text of Wikipedia parse HTML, without references and styles."""
    import html as _html
    h = re.sub(r"<style.*?</style>|<sup.*?</sup>", "", h, flags=re.S)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h)).replace("\xa0", " ").replace("​", "")).strip()
