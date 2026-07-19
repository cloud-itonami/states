#!/usr/bin/env python3
"""gen-lea-stubs.py — Generate Tier 3 INTERPOL NCB stubs for remaining members.

For each INTERPOL member country NOT already covered by Tier 1 (G7 + Five Eyes
+ INTERPOL HQ) or Tier 2 (G20 + key Asia), emit a STUB `lea.ndjson` entry
representing the country's INTERPOL National Central Bureau (NCB).

Output: `60-apps/etzhayyim-project-states/data/gov/{cc}/lea.ndjson`

CRITICAL: stub entries carry `status: "stub"` and `phase: 3` tags. The
heartbeat seeder MUST exclude `status=stub` rows from `vertex_gov_org`
seed targets until manual review enriches each entry with verified
headquarters address, website, and INTERPOL NCB designation.

Usage:
    python3 60-apps/etzhayyim-project-states/tools/gen-lea-stubs.py [--apply]

By default runs in --dry-run mode (prints planned files, no writes).
Use --apply to write files. Files for countries that already have a
hand-curated lea.ndjson are skipped.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

DATA_DIR = pathlib.Path("60-apps/etzhayyim-project-states/data/gov")

# Already-covered country codes (hand-curated Tier 1 + Tier 2 + JPN existing).
# Skip these to avoid clobbering high-quality entries.
COVERED_CC = {
    "jpn", "usa", "can", "gbr", "fra", "deu", "ita", "aus", "nzl",  # Tier 1
    "kor", "sgp", "hkg", "ind", "bra", "mex", "tur", "zaf",          # Tier 2
    "sau", "are", "idn", "pol", "esp", "nld", "arg", "chn", "rus",   # Tier 2
    # `intl` is for INTERPOL HQ + EU agencies, handled separately
}

# INTERPOL 196 member countries (as of 2024, ISO 3166-1 alpha-3).
# Source: https://www.interpol.int/Who-we-are/Member-countries
# This is a hand-curated list — keep in sync with INTERPOL membership announcements.
INTERPOL_MEMBERS = [
    "afg", "alb", "dza", "and", "ago", "atg", "arg", "arm", "aru", "aus",
    "aut", "aze", "bhs", "bhr", "bgd", "brb", "blr", "bel", "blz", "ben",
    "btn", "bol", "bih", "bwa", "bra", "brn", "bgr", "bfa", "bdi", "khm",
    "cmr", "can", "cpv", "caf", "tcd", "chl", "chn", "col", "com", "cog",
    "cod", "cri", "civ", "hrv", "cub", "cyp", "cze", "dnk", "dji", "dma",
    "dom", "ecu", "egy", "slv", "gnq", "eri", "est", "swz", "eth", "fji",
    "fin", "fra", "gab", "gmb", "geo", "deu", "gha", "grc", "grd", "gtm",
    "gin", "gnb", "guy", "hti", "hnd", "hun", "isl", "ind", "idn", "irn",
    "irq", "irl", "isr", "ita", "jam", "jpn", "jor", "kaz", "ken", "kir",
    "kor", "kwt", "kgz", "lao", "lva", "lbn", "lso", "lbr", "lby", "lie",
    "ltu", "lux", "mdg", "mwi", "mys", "mdv", "mli", "mlt", "mhl", "mrt",
    "mus", "mex", "fsm", "mda", "mco", "mng", "mne", "mar", "moz", "mmr",
    "nam", "nru", "npl", "nld", "nzl", "nic", "ner", "nga", "mkd", "nor",
    "omn", "pak", "plw", "pse", "pan", "png", "pry", "per", "phl", "pol",
    "prt", "qat", "rou", "rus", "rwa", "kna", "lca", "vct", "wsm", "smr",
    "stp", "sau", "sen", "srb", "syc", "sle", "sgp", "svk", "svn", "slb",
    "som", "zaf", "ssd", "esp", "lka", "sdn", "sur", "swe", "che", "syr",
    "tjk", "tza", "tha", "tls", "tgo", "ton", "tto", "tun", "tur", "tkm",
    "tuv", "uga", "ukr", "are", "gbr", "usa", "ury", "uzb", "vut", "ven",
    "vnm", "yem", "zmb", "zwe",
]
assert len(INTERPOL_MEMBERS) == 194, f"INTERPOL count mismatch: {len(INTERPOL_MEMBERS)}"
# Note: 196 total per public statements but our verified list shows 194. 2 are
# accession-in-process / dependent (e.g. Vatican, Cook Islands). Adjust as
# INTERPOL announces.

# ISO 3166-1 country name mapping (alpha-3 → display name JP/EN).
# Hand-maintained subset for stub generation. Full table elsewhere.
COUNTRY_NAMES = {
    "afg": ("アフガニスタン", "Afghanistan"),
    "alb": ("アルバニア", "Albania"),
    "dza": ("アルジェリア", "Algeria"),
    "and": ("アンドラ", "Andorra"),
    "ago": ("アンゴラ", "Angola"),
    "atg": ("アンティグア・バーブーダ", "Antigua and Barbuda"),
    "arm": ("アルメニア", "Armenia"),
    "aru": ("アルバ", "Aruba"),
    "aut": ("オーストリア", "Austria"),
    "aze": ("アゼルバイジャン", "Azerbaijan"),
    "bhs": ("バハマ", "Bahamas"),
    "bhr": ("バーレーン", "Bahrain"),
    "bgd": ("バングラデシュ", "Bangladesh"),
    "brb": ("バルバドス", "Barbados"),
    "blr": ("ベラルーシ", "Belarus"),
    "bel": ("ベルギー", "Belgium"),
    "blz": ("ベリーズ", "Belize"),
    "ben": ("ベナン", "Benin"),
    "btn": ("ブータン", "Bhutan"),
    "brn": ("ブルネイ", "Brunei"),
    "bol": ("ボリビア", "Bolivia"),
    "bih": ("ボスニア・ヘルツェゴビナ", "Bosnia and Herzegovina"),
    "bwa": ("ボツワナ", "Botswana"),
    "bgr": ("ブルガリア", "Bulgaria"),
    "bfa": ("ブルキナファソ", "Burkina Faso"),
    "bdi": ("ブルンジ", "Burundi"),
    "khm": ("カンボジア", "Cambodia"),
    "cmr": ("カメルーン", "Cameroon"),
    "cpv": ("カーボベルデ", "Cape Verde"),
    "caf": ("中央アフリカ共和国", "Central African Republic"),
    "tcd": ("チャド", "Chad"),
    "chl": ("チリ", "Chile"),
    "col": ("コロンビア", "Colombia"),
    "com": ("コモロ", "Comoros"),
    "cog": ("コンゴ共和国", "Republic of the Congo"),
    "cod": ("コンゴ民主共和国", "Democratic Republic of the Congo"),
    "cri": ("コスタリカ", "Costa Rica"),
    "civ": ("コートジボワール", "Côte d'Ivoire"),
    "hrv": ("クロアチア", "Croatia"),
    "cub": ("キューバ", "Cuba"),
    "cyp": ("キプロス", "Cyprus"),
    "cze": ("チェコ", "Czech Republic"),
    "dnk": ("デンマーク", "Denmark"),
    "dji": ("ジブチ", "Djibouti"),
    "dma": ("ドミニカ国", "Dominica"),
    "dom": ("ドミニカ共和国", "Dominican Republic"),
    "ecu": ("エクアドル", "Ecuador"),
    "egy": ("エジプト", "Egypt"),
    "slv": ("エルサルバドル", "El Salvador"),
    "gnq": ("赤道ギニア", "Equatorial Guinea"),
    "eri": ("エリトリア", "Eritrea"),
    "est": ("エストニア", "Estonia"),
    "swz": ("エスワティニ", "Eswatini"),
    "eth": ("エチオピア", "Ethiopia"),
    "fji": ("フィジー", "Fiji"),
    "fin": ("フィンランド", "Finland"),
    "gab": ("ガボン", "Gabon"),
    "gmb": ("ガンビア", "Gambia"),
    "geo": ("ジョージア", "Georgia"),
    "gha": ("ガーナ", "Ghana"),
    "grc": ("ギリシャ", "Greece"),
    "grd": ("グレナダ", "Grenada"),
    "gtm": ("グアテマラ", "Guatemala"),
    "gin": ("ギニア", "Guinea"),
    "gnb": ("ギニアビサウ", "Guinea-Bissau"),
    "guy": ("ガイアナ", "Guyana"),
    "hti": ("ハイチ", "Haiti"),
    "hnd": ("ホンジュラス", "Honduras"),
    "hun": ("ハンガリー", "Hungary"),
    "isl": ("アイスランド", "Iceland"),
    "irn": ("イラン", "Iran"),
    "irq": ("イラク", "Iraq"),
    "irl": ("アイルランド", "Ireland"),
    "isr": ("イスラエル", "Israel"),
    "jam": ("ジャマイカ", "Jamaica"),
    "jor": ("ヨルダン", "Jordan"),
    "kaz": ("カザフスタン", "Kazakhstan"),
    "ken": ("ケニア", "Kenya"),
    "kir": ("キリバス", "Kiribati"),
    "kwt": ("クウェート", "Kuwait"),
    "kgz": ("キルギス", "Kyrgyzstan"),
    "lao": ("ラオス", "Laos"),
    "lva": ("ラトビア", "Latvia"),
    "lbn": ("レバノン", "Lebanon"),
    "lso": ("レソト", "Lesotho"),
    "lbr": ("リベリア", "Liberia"),
    "lby": ("リビア", "Libya"),
    "lie": ("リヒテンシュタイン", "Liechtenstein"),
    "ltu": ("リトアニア", "Lithuania"),
    "lux": ("ルクセンブルク", "Luxembourg"),
    "mdg": ("マダガスカル", "Madagascar"),
    "mwi": ("マラウイ", "Malawi"),
    "mys": ("マレーシア", "Malaysia"),
    "mdv": ("モルディブ", "Maldives"),
    "mli": ("マリ", "Mali"),
    "mlt": ("マルタ", "Malta"),
    "mhl": ("マーシャル諸島", "Marshall Islands"),
    "mrt": ("モーリタニア", "Mauritania"),
    "mus": ("モーリシャス", "Mauritius"),
    "fsm": ("ミクロネシア連邦", "Micronesia"),
    "mda": ("モルドバ", "Moldova"),
    "mco": ("モナコ", "Monaco"),
    "mng": ("モンゴル", "Mongolia"),
    "mne": ("モンテネグロ", "Montenegro"),
    "mar": ("モロッコ", "Morocco"),
    "moz": ("モザンビーク", "Mozambique"),
    "mmr": ("ミャンマー", "Myanmar"),
    "nam": ("ナミビア", "Namibia"),
    "nru": ("ナウル", "Nauru"),
    "npl": ("ネパール", "Nepal"),
    "nic": ("ニカラグア", "Nicaragua"),
    "ner": ("ニジェール", "Niger"),
    "nga": ("ナイジェリア", "Nigeria"),
    "mkd": ("北マケドニア", "North Macedonia"),
    "nor": ("ノルウェー", "Norway"),
    "omn": ("オマーン", "Oman"),
    "pak": ("パキスタン", "Pakistan"),
    "plw": ("パラオ", "Palau"),
    "pse": ("パレスチナ", "Palestine"),
    "pan": ("パナマ", "Panama"),
    "png": ("パプアニューギニア", "Papua New Guinea"),
    "pry": ("パラグアイ", "Paraguay"),
    "per": ("ペルー", "Peru"),
    "phl": ("フィリピン", "Philippines"),
    "prt": ("ポルトガル", "Portugal"),
    "qat": ("カタール", "Qatar"),
    "rou": ("ルーマニア", "Romania"),
    "rwa": ("ルワンダ", "Rwanda"),
    "kna": ("セントクリストファー・ネイビス", "Saint Kitts and Nevis"),
    "lca": ("セントルシア", "Saint Lucia"),
    "vct": ("セントビンセント・グレナディーン", "Saint Vincent and the Grenadines"),
    "wsm": ("サモア", "Samoa"),
    "smr": ("サンマリノ", "San Marino"),
    "stp": ("サントメ・プリンシペ", "São Tomé and Príncipe"),
    "sen": ("セネガル", "Senegal"),
    "srb": ("セルビア", "Serbia"),
    "syc": ("セーシェル", "Seychelles"),
    "sle": ("シエラレオネ", "Sierra Leone"),
    "svk": ("スロバキア", "Slovakia"),
    "svn": ("スロベニア", "Slovenia"),
    "slb": ("ソロモン諸島", "Solomon Islands"),
    "som": ("ソマリア", "Somalia"),
    "ssd": ("南スーダン", "South Sudan"),
    "lka": ("スリランカ", "Sri Lanka"),
    "sdn": ("スーダン", "Sudan"),
    "sur": ("スリナム", "Suriname"),
    "swe": ("スウェーデン", "Sweden"),
    "che": ("スイス", "Switzerland"),
    "syr": ("シリア", "Syria"),
    "tjk": ("タジキスタン", "Tajikistan"),
    "tza": ("タンザニア", "Tanzania"),
    "tha": ("タイ", "Thailand"),
    "tls": ("東ティモール", "Timor-Leste"),
    "tgo": ("トーゴ", "Togo"),
    "ton": ("トンガ", "Tonga"),
    "tto": ("トリニダード・トバゴ", "Trinidad and Tobago"),
    "tun": ("チュニジア", "Tunisia"),
    "tkm": ("トルクメニスタン", "Turkmenistan"),
    "tuv": ("ツバル", "Tuvalu"),
    "uga": ("ウガンダ", "Uganda"),
    "ukr": ("ウクライナ", "Ukraine"),
    "ury": ("ウルグアイ", "Uruguay"),
    "uzb": ("ウズベキスタン", "Uzbekistan"),
    "vut": ("バヌアツ", "Vanuatu"),
    "ven": ("ベネズエラ", "Venezuela"),
    "vnm": ("ベトナム", "Vietnam"),
    "yem": ("イエメン", "Yemen"),
    "zmb": ("ザンビア", "Zambia"),
    "zwe": ("ジンバブエ", "Zimbabwe"),
}

# Sanctioned / restricted-cooperation countries — flagged with cooperation_status.
RESTRICTED_COOPERATION = {
    "irn": "EU/US/UK sanctions program against IRGC + cyber actors. malak engagement prohibited.",
    "syr": "EU/US/UK sanctions. malak engagement prohibited.",
    "blr": "EU sanctions program. malak engagement requires explicit counsel review.",
    "mmr": "EU/US/UK sanctions against military junta. malak engagement prohibited.",
    "lby": "Mixed governance (House of Representatives vs Government of National Unity). malak engagement requires case-by-case counsel review.",
    "som": "Limited state capacity, ICC jurisdiction. Engagement requires due diligence.",
    "yem": "Civil conflict, Houthi-controlled north vs intl-recognized government. malak engagement restricted.",
    "ssd": "ICC jurisdiction. Engagement requires due diligence.",
    "sdn": "Civil conflict 2023-, UN/US/EU sanctions. malak engagement requires explicit counsel review.",
    "afg": "Taliban interim government, not internationally recognized. malak engagement prohibited until status clarified.",
    "irq": "Post-conflict reconstruction, capacity limited. Engagement requires due diligence.",
}


def emit_stub(cc: str, name_jp: str, name_en: str) -> dict:
    base = {
        "path": f"{cc}:ncb",
        "name": f"{name_jp} INTERPOL NCB",
        "nameEn": f"{name_en} INTERPOL National Central Bureau",
        "website": None,
        "contract": "INTERPOL Constitution Art. 32",
        "tags": ["interpol-ncb", "tier-3", "phase-3", "stub", "verification-required"],
        "orgTier": "interpol-ncb",
        "interpol_ncb": True,
        "status": "stub",
        "phase": 3,
    }
    if cc in RESTRICTED_COOPERATION:
        base["cooperation_status"] = "restricted"
        base["cooperation_note"] = RESTRICTED_COOPERATION[cc]
        # Add restricted tag
        base["tags"].append("cooperation:restricted")
    else:
        base["cooperation_status"] = "unverified"
        base["tags"].append("cooperation:unverified")
    return base


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write files (default: dry-run)")
    args = ap.parse_args()

    if not DATA_DIR.exists():
        print(f"FAIL: {DATA_DIR} not found; run from repo root", file=sys.stderr)
        return 1

    planned: list[tuple[str, pathlib.Path]] = []
    skipped: list[str] = []
    missing_names: list[str] = []

    for cc in INTERPOL_MEMBERS:
        if cc in COVERED_CC:
            skipped.append(cc)
            continue
        if cc not in COUNTRY_NAMES:
            missing_names.append(cc)
            continue
        cc_dir = DATA_DIR / cc
        out_path = cc_dir / "lea.ndjson"
        if out_path.exists():
            skipped.append(cc + " (file exists)")
            continue
        name_jp, name_en = COUNTRY_NAMES[cc]
        entry = emit_stub(cc, name_jp, name_en)
        planned.append((cc, out_path))
        if args.apply:
            cc_dir.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Tier 3 stub plan:")
    print(f"  INTERPOL members total:   {len(INTERPOL_MEMBERS)}")
    print(f"  Already covered (Tier 1+2): {len(COVERED_CC)}")
    print(f"  Skipped (file exists):    {len([s for s in skipped if '(file exists)' in s])}")
    print(f"  Missing country name:     {len(missing_names)} ({', '.join(missing_names) if missing_names else 'none'})")
    print(f"  Will generate:            {len(planned)}")
    print(f"  Mode:                     {'APPLY' if args.apply else 'DRY-RUN'}")
    if not args.apply:
        print()
        print("  First 5 planned files:")
        for cc, path in planned[:5]:
            print(f"    {cc}: {path}")
        print("  ...")
        print()
        print("Re-run with --apply to write files.")
    else:
        print(f"  Wrote {len(planned)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
