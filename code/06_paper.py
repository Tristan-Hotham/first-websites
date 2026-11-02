"""Build the paper: fill code/paper_template.tex from data/results.json and data/site.json, add tables, compile with
xelatex. Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them). The DOI stays as the 10.5281/zenodo.23878602
placeholder. Needs only data/."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json"); S = jload(f"{DATA}/site.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_First_Websites"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# statements made in words in the paper only
assert R["firsts"]["new_by_year"]["1992"] == 5 and R["firsts"]["new_by_year"]["1993"] == max(R["firsts"]["new_by_year"].values())
assert R["list"]["types"]["Fans, hobbies and fun"] == max(R["list"]["types"].values())
assert len(R["cctld"]["disagree"]) == 3


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "pc1": return f"{float(v):.1f}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f in ("word", "Word"): return fmt(v, f)
    return tex(str(v))


L = R["list"]
rows = "".join(f"{tex(t)} & {L['types'][t]} & {L['types_pct'][t]:.1f}\\% & {L['type_status'][t]['live']} & {L['type_status'][t]['gone']} & {L['year_type']['1991'][t] + L['year_type']['1992'][t]} & {L['year_type']['1993'][t]} & {L['year_type']['1994'][t]}\\\\\n" for t in TN)
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{The pre-1995 list by kind of website (my coding): count, share, what the text says about status, and year.}\\label{tab:types}"
      "\\begin{tabular}{lrrrrrrr}\\toprule Kind & Sites & Share & Online & Closed & 1991 to 1992 & 1993 & 1994\\\\\\midrule\n" + rows +
      f"\\midrule All & {L['n']} & 100\\% & {L['live']} & {L['gone']} & {L['n_9192']} & {L['by_year']['1993']} & {L['by_year']['1994']}\\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
rows = "".join(f"{tex(r['country'])} & {r['y']}{'?' if r['doubt'] else ''} & {tex(r['name'][:46])} & {'list' if r['src'] == 'list' else 'Wikidata'} & {S['cctld'].get(r['iso'], ['', ''])[0]} {S['cctld'].get(r['iso'], ['', ''])[1]}\\\\\n" for r in R["firsts"]["rows"])
TF = ("\\begin{small}\\begin{longtable}{lrp{6.2cm}ll}\\caption{Earliest recorded website in each country. ? = dated before the country's own domain. Last column: country code domain and its Wikidata year.}\\label{tab:firsts}\\\\"
      "\\toprule Country & Year & Website & Source & Domain\\\\\\midrule\\endfirsthead\\toprule Country & Year & Website & Source & Domain\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{small}")
cn = lambda i: S["cn"][i][0] if i else "not known"
ST = {"live": "online", "gone": "closed", "": "not stated"}
rows = "".join(f"{tex(r[1][:40])} & {r[2]} & {tex(cn(r[3]))} & {tex(TN[r[6]])} & {ST[r[7]]}\\\\\n" for r in S["list"])
TL = ("\\begin{footnotesize}\\begin{longtable}{p{4.6cm}rp{2.8cm}p{4.3cm}l}\\caption{Wikipedia's list of websites founded before 1995 as coded here: year section, country, kind and status in the text.}\\label{tab:list}\\\\"
      "\\toprule Website & Year & Country & Kind & Status\\\\\\midrule\\endfirsthead\\toprule Website & Year & Country & Kind & Status\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{footnotesize}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = t.replace("\\href{https://doi.org/{{meta.doi}}}{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("TYPES", TT), ("FIRSTS", TF), ("LIST", TL)):
    t = t.replace("{{TABLE_%s}}" % k, v)
assert "{{" not in t.replace("\\{\\{DOI\\}\\}", "") and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
