#!/usr/bin/env python3
"""
Generate data/gov/{cc}/{tier}.ndjson from component-registry.json.
Run from the etzhayyim-project-states/ directory.

Layout mirrors DID path:
  data/gov/{cc}/ministry.ndjson  → did:web:gov-{cc}.etzhayyim.com:{ministry-path}
  data/gov/{cc}/district.ndjson  → did:web:gov-{cc}.etzhayyim.com:district:{slug}
  data/gov/intl/agency.ndjson    → did:web:gov-intl.etzhayyim.com:{slug}
"""
import json, os, re, pathlib

SRC = pathlib.Path("tools/component-registry.json")
OUT = pathlib.Path("data/gov")

# ── Known official websites (G20 + major countries) ──────────────────────────
# key = "{cc}:{org-slug-keyword}"  (partial match on short field)
KNOWN_WEBSITES: dict[str, str] = {
    # USA
    "usa:white-house":            "https://www.whitehouse.gov/",
    "usa:department-of-defense":  "https://www.defense.gov/",
    "usa:department-of-state":    "https://www.state.gov/",
    "usa:department-of-treasury": "https://home.treasury.gov/",
    "usa:department-of-justice":  "https://www.justice.gov/",
    "usa:department-of-homeland": "https://www.dhs.gov/",
    "usa:department-of-energy":   "https://www.energy.gov/",
    "usa:department-of-education":"https://www.ed.gov/",
    "usa:department-of-health":   "https://www.hhs.gov/",
    "usa:department-of-transport":"https://www.transportation.gov/",
    "usa:department-of-commerce": "https://www.commerce.gov/",
    "usa:department-of-labor":    "https://www.dol.gov/",
    "usa:department-of-interior": "https://www.doi.gov/",
    "usa:department-of-agriculture":"https://www.usda.gov/",
    "usa:department-of-housing":  "https://www.hud.gov/",
    "usa:department-of-veteran":  "https://www.va.gov/",
    # CHN
    "chn:state-council":          "https://english.www.gov.cn/",
    "chn:ministry-of-foreign":    "https://www.mfa.gov.cn/",
    "chn:ministry-of-defense":    "http://www.mod.gov.cn/",
    "chn:ministry-of-finance":    "http://www.mof.gov.cn/",
    "chn:ministry-of-justice":    "http://www.moj.gov.cn/",
    "chn:national-development":   "https://www.ndrc.gov.cn/",
    # DEU
    "deu:federal-chancellery":    "https://www.bundesregierung.de/",
    "deu:federal-foreign":        "https://www.auswaertiges-amt.de/",
    "deu:federal-ministry-of-finance":"https://www.bundesfinanzministerium.de/",
    "deu:federal-ministry-of-defense":"https://www.bmvg.de/",
    "deu:federal-ministry-of-justice":"https://www.bmj.de/",
    "deu:federal-ministry-of-interior":"https://www.bmi.bund.de/",
    "deu:federal-ministry-of-economy":"https://www.bmwk.de/",
    # GBR
    "gbr:cabinet-office":         "https://www.gov.uk/government/organisations/cabinet-office",
    "gbr:foreign-commonwealth":   "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office",
    "gbr:hm-treasury":            "https://www.gov.uk/government/organisations/hm-treasury",
    "gbr:ministry-of-defence":    "https://www.gov.uk/government/organisations/ministry-of-defence",
    "gbr:ministry-of-justice":    "https://www.gov.uk/government/organisations/ministry-of-justice",
    "gbr:home-office":            "https://www.gov.uk/government/organisations/home-office",
    # FRA
    "fra:elysee":                 "https://www.elysee.fr/",
    "fra:ministere-des-armees":   "https://www.defense.gouv.fr/",
    "fra:ministere-de-economie":  "https://www.economie.gouv.fr/",
    "fra:ministere-des-affaires": "https://www.diplomatie.gouv.fr/",
    "fra:ministere-de-justice":   "https://www.justice.gouv.fr/",
    "fra:ministere-de-interieur": "https://www.interieur.gouv.fr/",
    # ITA
    "ita:presidenza-del-consiglio":"https://www.governo.it/",
    "ita:ministero-della-difesa": "https://www.difesa.it/",
    "ita:ministero-degli-esteri": "https://www.esteri.it/",
    "ita:ministero-dell-economia":"https://www.mef.gov.it/",
    "ita:ministero-della-giustizia":"https://www.giustizia.it/",
    # CAN
    "can:privy-council":          "https://www.canada.ca/en/privy-council.html",
    "can:department-of-national": "https://www.canada.ca/en/department-national-defence.html",
    "can:department-of-foreign":  "https://www.international.gc.ca/",
    "can:department-of-finance":  "https://www.canada.ca/en/department-finance.html",
    "can:department-of-justice":  "https://www.justice.gc.ca/",
    # AUS
    "aus:department-of-prime":    "https://www.pmc.gov.au/",
    "aus:department-of-defence":  "https://www.defence.gov.au/",
    "aus:department-of-foreign":  "https://www.dfat.gov.au/",
    "aus:department-of-treasury": "https://www.treasury.gov.au/",
    "aus:attorney-general":       "https://www.ag.gov.au/",
    # KOR
    "kor:cheong-wa-dae":          "https://www.president.go.kr/",
    "kor:ministry-of-defense":    "https://www.mnd.go.kr/",
    "kor:ministry-of-foreign":    "https://www.mofa.go.kr/",
    "kor:ministry-of-economy":    "https://www.moef.go.kr/",
    "kor:ministry-of-justice":    "https://www.moj.go.kr/",
    "kor:ministry-of-interior":   "https://www.mois.go.kr/",
    # IND
    "ind:prime-minister":         "https://www.pmindia.gov.in/",
    "ind:ministry-of-defence":    "https://www.mod.gov.in/",
    "ind:ministry-of-external":   "https://www.mea.gov.in/",
    "ind:ministry-of-finance":    "https://www.finmin.nic.in/",
    "ind:ministry-of-home":       "https://www.mha.gov.in/",
    "ind:ministry-of-law":        "https://lawmin.gov.in/",
    # BRA
    "bra:presidencia":            "https://www.gov.br/presidencia/",
    "bra:ministerio-da-defesa":   "https://www.gov.br/defesa/",
    "bra:ministerio-das-relacoes":"https://www.gov.br/mre/",
    "bra:ministerio-da-fazenda":  "https://www.gov.br/fazenda/",
    "bra:ministerio-da-justica":  "https://www.gov.br/mj/",
    # RUS
    "rus:kremlin":                "http://www.kremlin.ru/",
    "rus:ministry-of-defence":    "https://eng.mil.ru/",
    "rus:ministry-of-foreign":    "https://www.mid.ru/",
    "rus:ministry-of-finance":    "https://minfin.gov.ru/",
    "rus:ministry-of-justice":    "https://minjust.gov.ru/",
    # MEX
    "mex:presidencia":            "https://www.gob.mx/presidencia",
    "mex:secretaria-de-defensa":  "https://www.gob.mx/sedena",
    "mex:secretaria-de-relaciones":"https://www.gob.mx/sre",
    "mex:secretaria-de-hacienda": "https://www.gob.mx/shcp",
    "mex:secretaria-de-gobernacion":"https://www.gob.mx/segob",
    # SAU
    "sau:council-of-ministers":   "https://www.saudi.gov.sa/",
    "sau:ministry-of-defense":    "https://www.mod.gov.sa/",
    "sau:ministry-of-foreign":    "https://www.mofa.gov.sa/",
    # TUR
    "tur:cumhurbaskanligi":       "https://www.tccb.gov.tr/",
    "tur:milli-savunma":          "https://www.msb.gov.tr/",
    "tur:disisleri":              "https://www.mfa.gov.tr/",
    "tur:hazine-ve-maliye":       "https://www.hmb.gov.tr/",
    # ARG
    "arg:presidencia":            "https://www.argentina.gob.ar/presidencia",
    # ZAF
    "zaf:the-presidency":         "https://www.thepresidency.gov.za/",
    "zaf:department-of-defence":  "https://www.dod.mil.za/",
    # IDN
    "idn:sekretariat-negara":     "https://www.setneg.go.id/",
    "idn:kementerian-pertahanan": "https://www.kemhan.go.id/",
    # intl
    "intl:united-nations":        "https://www.un.org/",
    "intl:world-bank":            "https://www.worldbank.org/",
    "intl:imf":                   "https://www.imf.org/",
    "intl:who":                   "https://www.who.int/",
    "intl:wto":                   "https://www.wto.org/",
    "intl:nato":                  "https://www.nato.int/",
    "intl:oecd":                  "https://www.oecd.org/",
    "intl:iaea":                  "https://www.iaea.org/",
    "intl:ilo":                   "https://www.ilo.org/",
    "intl:icj":                   "https://www.icj-cij.org/",
    "intl:interpol":              "https://www.interpol.int/",
    "intl:imo":                   "https://www.imo.org/",
    "intl:wipo":                  "https://www.wipo.int/",
}

# COFOG code → contract hint
COFOG_CONTRACT: dict[str, str] = {
    "01":   "General Public Services Act",
    "01.6": "General Public Services Act",
    "02":   "Defence Act",
    "03":   "Public Order and Safety Act",
    "04":   "Economic Affairs Act",
    "04.2": "Agriculture Act",
    "04.5": "Transport Act",
    "05":   "Environmental Protection Act",
    "06":   "Housing Act",
    "07":   "Health Act",
    "08":   "Recreation Act",
    "09":   "Education Act",
    "10":   "Social Protection Act",
    "intl": "International Treaty",
}

# orgTier → ndjson file name
TIER_FILE: dict[str, str] = {
    "ministry":      "ministry",
    "executive":     "ministry",
    "department":    "ministry",
    "office":        "office",
    "district":      "district",
    "international": "ministry",
}

NANOID_RE = re.compile(r"-[a-z0-9]{6,8}$")  # trailing nanoid suffix e.g. "-k2p8cu2n"

def strip_nanoid(s: str) -> str:
    """Remove trailing nanoid suffix from slug."""
    return NANOID_RE.sub("", s)

def slug_to_path(cc: str, short: str, tier: str) -> str:
    """Convert short name + tier to a DID-compatible path segment."""
    s = re.sub(r"^\d+-", "", short)           # strip leading digits (e.g. "0-")
    s = re.sub(r"^" + re.escape(cc) + r"-", "", s)  # strip cc prefix
    s = strip_nanoid(s)
    s = s.strip("-")
    if tier == "district":
        return f"district:{s}"
    return s

def find_website(cc: str, short: str) -> str:
    """Look up known website by partial key match."""
    clean = strip_nanoid(short)
    for key, url in KNOWN_WEBSITES.items():
        k_cc, k_kw = key.split(":", 1)
        if k_cc != cc:
            continue
        if k_kw in clean:
            return url
    return ""

def short_to_name(short: str, cc: str) -> str:
    """Convert slug to a title-cased display name."""
    s = re.sub(r"^\d+-", "", short)
    s = re.sub(r"^" + re.escape(cc) + r"-", "", s)
    s = strip_nanoid(s)
    return s.replace("-", " ").title()

def main() -> None:
    src = json.loads(SRC.read_text())
    components: list[dict] = src["components"]

    # Group by cc → tier
    from collections import defaultdict
    groups: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for comp in components:
        cc = comp.get("countryCode", "").lower()
        tier = comp.get("orgTier", "office")
        groups[cc][tier].append(comp)

    created_files = 0
    created_records = 0

    for cc, tiers in sorted(groups.items()):
        cc_dir = OUT / cc
        cc_dir.mkdir(parents=True, exist_ok=True)

        # Group by output file
        file_records: dict[str, list[str]] = defaultdict(list)
        path_seen: dict[str, dict[str, int]] = defaultdict(dict)  # fname → path → count

        for tier, comps in tiers.items():
            fname = TIER_FILE.get(tier, "office")
            for comp in comps:
                short = comp.get("short", "")
                cofog = comp.get("cofogCode", "01")
                name_en = short_to_name(short, cc)
                path = slug_to_path(cc, short, tier)
                website = find_website(cc, short)
                contract = COFOG_CONTRACT.get(cofog, "Government Act")
                tags = [
                    f"cofog:{cofog}",
                    comp.get("cofogName", "general-public-services"),
                    tier,
                ]
                if comp.get("nanoid"):
                    tags.append(f"nanoid:{comp['nanoid']}")

                # Deduplicate within file: append counter on collision
                seen_in_file = path_seen[fname]
                if path in seen_in_file:
                    n = seen_in_file[path] + 1
                    path = f"{path}-{n}"
                seen_in_file[path] = seen_in_file.get(path, 0) + 1

                record = {
                    "path":     path,
                    "name":     name_en,  # English only; LLM can add local name
                    "nameEn":   name_en,
                    "website":  website,
                    "contract": contract,
                    "tags":     tags,
                    "orgTier":  tier,
                    "cofogCode": cofog,
                    "countryCode": cc,
                }
                file_records[fname].append(json.dumps(record, ensure_ascii=False))

        for fname, lines in file_records.items():
            # Skip if jpn/* — already hand-crafted
            if cc == "jpn":
                print(f"  skip jpn/{fname}.ndjson (hand-crafted)")
                continue
            out_path = cc_dir / f"{fname}.ndjson"
            out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            created_files += 1
            created_records += len(lines)
            print(f"  {out_path}  ({len(lines)} records)")

    print(f"\nDone: {created_files} files, {created_records} records")

if __name__ == "__main__":
    main()
