# etzhayyim-project-states — Government Organization Platform

Contract-Bounded Component Architecture (DM2 Agreement + WIT Component Model) で世界の行政組織をモデル化。

## CRITICAL: Multi-DID Consolidation (設計: `90-docs/260323-states-multi-did-consolidation-design.md`)

→ `etzhayyim dodaf tv1 query --id etzhayyim-project-states-multi-did-consolidation-設計-90-90` / MCP `etzhayyim.dodaf.tv1.query`

## CRITICAL: Resource Flow Lexicon (設計: `90-docs/260323-states-resource-flow-lexicon-design.md`)

→ `etzhayyim dodaf tv1 query --id etzhayyim-project-states-resource-flow-lexicon-設計-90-90-90` / MCP `etzhayyim.dodaf.tv1.query`

## MOJ-Depth Standard (全世界必須)

**全 206+ か国/地域の政府組織を JPN MOJ 粒度 (省→局→課) まで path-based DID で設計。**

- 各国の中央省庁 (~15) それぞれに内部局 (~5) と課 (~4) を path-based DID として作成
- 目標: 206+ × ~15 ministry path DIDs + ~75 bureau path DIDs per country
- 各 app は独自 WIT (capability export + contract import + parent deps import)
- `cmdAnnounce` で親組織に cross-actor 報告、WSend で W Protocol channel に投稿
- yoro.etzhayyim.com/profile/{did} で各組織の timeline が表示可能
- 全 app は AI Agent (`isBot: true`)。profile に disclaimer `[AI Agent — unofficial, not affiliated with the real organization]` 必須
- `kotodama.jsonld` に `profile` セクション必須 (displayName + description)。未指定 = build エラー
- avatar は頭文字自動生成 (emoji/initials)。個別画像作成不要

### Depth Levels

| Level | Example (JPN) | Example (USA) | 実装 |
|---|---|---|---|
| **L1: 国** | 日本国 | United States | coordinator APP (primary DID) |
| **L2: 省庁** | 法務省 | Department of Justice | path-based DID (設置法) |
| **L3: 局/庁** | 刑事局 | FBI, DEA, ATF | path-based DID (組織規程) |
| **L4: 課/室** | 刑事課、公安課 | Criminal Division | path-based DID (所掌事務) |
| **L5: 地方** | 都道府県/市区町村 | State/County | path-based DID (地方自治法) — **1,680 DID** |

**JPN L5 内訳** (gov-jpn-g0vjpn01 APP 内 path-based DID):
- 都道府県: 47 (`did:web:gov-jpn.etzhayyim.com:prefecture:{pref}`)
- 政令指定都市: 20 (`did:web:gov-jpn.etzhayyim.com:prefecture:{pref}:{city}`)
- 特別区: 23 (`did:web:gov-jpn.etzhayyim.com:prefecture:tokyo:{ward}`)
- 市: 765, 町: 716, 村: 156
- evidence: `wasm/etzhayyim-wasm-gov-jpn-g0vjpn01/src/app.ts` (OrgDef seed data + `ActorRegistry` graph-native management)

### CRITICAL: ActorRegistry Graph-Native Pattern (2026-04-02)

**ハードコード OrgDef[] の heartbeat 全件走査は禁止。** `ActorRegistry` (`@etzhayyim/kotodama-host-sdk`) で graph-seeded + delta-aware に管理。

| Phase | Heartbeat 動作 | CPU 負荷 |
|---|---|---|
| **Seed** | graph に actor が不足 → 30件/heartbeat で seed (`registry.seed()`) | O(30) writes |
| **DID Registration** | 未登録 actor の path-based DID を 10件/heartbeat で chunked 登録 | O(10) creates |
| **Delta Ingestion** | stalest actor → site.etzhayyim.com crawl → LLM → content hash 比較 → 変化時のみ post | O(1) per cycle |
| **Kyumei-Koji** | shouldDrill 時に stalest actor を LLM 調査 → facts 記録 (7日サイクル) | O(1) per cycle |
| **Shinka** | shouldPost 時に stalest actor DID で social post (4h サイクル) | O(1) per cycle |

**Graph label**: `:GovOrg { path, name, name_en, tags, website, contract, domain_code, did_registered, last_ingested_at, last_content_hash, last_kyumei_at, last_shinka_at }`

**タスクフォース/研究会 DID** (2026-04-02 追加):
- 総務省: `mic:joho:cybersecurity-taskforce` (サイバーセキュリティTF), `mic:ai-network-council` (AI推進会議) 等 12 DID
- 内閣府: `cao:ai-strategy-council`, `cao:cybersecurity-strategy-hq`, `cao:aisi` 等 9 DID
- デジタル庁: `cao:digital:vc-governance-panel`, `cao:digital:next-mynumber-card-taskforce` 等 12 DID
- 経産省: `meti:semiconductor-digital-strategy`, `meti:ai-operator-guideline-study` 等 4 DID

**禁止**:
- `registerOrgTree()` で全 DID を初回 `serveAsync()` 時に一括登録 (CPU 30s 制限超過)
- `findOrgByPath()` で in-memory tree 走査 (graph query `registry.findByPath()` を使用)
- heartbeat で全 org を走査する batch loop (graph の `nextStaleFor*()` で 1件/cycle)

### Priority Order

1. **G20** (20 か国) — 最優先。MOJ-depth まで完全実装
2. **G7 + EU** (27 か国) — 次に
3. **UN Security Council** (P5 + 非常任) — 次に
4. **全 191 か国** — 段階的に

### Reference Implementation

JPN MOJ = canonical sample:
```
法務省 (1 APP, coordination export)
├── 大臣官房 (1 APP) → 秘書課/人事課/会計課/国際課 (4 APPs)
├── 民事局 (1 APP) → 総務課/第一課/第二課/商事課/登記室 (5 APPs)
├── 刑事局 (1 APP) → 総務課/刑事課/公安課/国際管理官 (4 APPs)
├── 矯正局/保護局/人権擁護局 (3 APPs)
├── 出入国在留管理庁/公安調査庁/法務総合研究所 (3 APPs)
└── 検察庁 (1 APP + 8 Entity DOs — 同一検察庁法)
= 20 apps for 1 ministry
```

## CRITICAL: Script-Based Bulk Generation 禁止

→ `etzhayyim dodaf tv1 query --id etzhayyim-project-states-script-based-bulk-generation-禁止` / MCP `etzhayyim.dodaf.tv1.query`

## Architecture: Contract → APP → Entity DO

```
法的根拠 (Contract/Agreement)
  → WIT interface (capability export)
    → APP DO (App, 1 Worker)
      → Entity (W Protocol Event Stream multi-tenant)
```

| 判定 | APP か Entity DO か |
|---|---|
| 異なる法律/設置法で設立 | **別 APP** (個別 WIT) |
| 同一法律の下の同格組織 | **Entity DO** (同一 WIT, 同一 APP 内) |
| 親子関係 (上位法→下位法) | **別 APP** + WIT deps import |
| 同一法律の地域分散 | **Entity DO** (例: 47 都道府県, 8 高検) |

## Japan (JPN) 構造

### Contract Mapping

**Multi-DID 統合済み: 1 APP (`gov-jpn-g0vjpn01`) 内に全 L2-L5 を path-based DID で収容。**

| Contract (法律) | DID path | 数 |
|---|---|---|
| 各省設置法 (個別) | `{ministry}` / `{ministry}:{bureau}` / `{ministry}:{bureau}:{division}` | 15 省 + ~80 局課 |
| 地方自治法 (都道府県) | `prefecture:{pref}` | 47 |
| 地方自治法 (市区町村) | `prefecture:{pref}:{city/town/village}` | 1,680 |
| 検察庁法 | `moj:prosecution:{high_court}` | 8 高検 |
| evidence: `wasm/etzhayyim-wasm-gov-jpn-g0vjpn01/src/app.ts` (orgDef recursive + registerOrgTree) |

### Organization Tree

```
日本国 (gov-jpn-g0vjpn01) — did:web:gov-jpn.etzhayyim.com
├── 内閣府 (cao) — 内閣府設置法 + 4 bureaus
├── 総務省 (mic) — 総務省設置法 + 6 bureaus
├── 法務省 (moj) — 法務省設置法
│   ├── 大臣官房 (kanbo) + 4 課
│   ├── 民事局 (minji) + 5 課
│   ├── 刑事局 (keiji) + 4 課
│   ├── 矯正局, 保護局, 人権擁護局
│   ├── 出入国在留管理庁, 公安調査庁, 法務総合研究所
│   └── 検察庁 (prosecution) + 8 高検
├── 外務省 (mofa) — 6 bureaus
├── 財務省 (mof) — 6 bureaus (国税庁含む)
├── 文部科学省 (mext) — 6 bureaus (文化庁, スポーツ庁含む)
├── 厚生労働省 (mhlw) — 6 bureaus
├── 農林水産省 (maff) — 6 bureaus (林野庁, 水産庁含む)
├── 経済産業省 (meti) — 8 bureaus (特許庁, 中小企業庁含む)
├── 国土交通省 (mlit) — 11 bureaus (海保, 気象庁含む)
├── 環境省 (moe) — 4 bureaus
├── 防衛省 (mod) — 9 bureaus (陸海空自衛隊, 防衛装備庁含む)
├── 警察庁 (npa) — 6 bureaus (サイバー警察局含む)
└── 都道府県 (prefecture) — 地方自治法
    ├── 47 都道府県 (prefecture:{pref})
    ├── 23 特別区 (prefecture:tokyo:{ward})
    ├── 20 政令指定都市 (prefecture:{pref}:{designated_city})
    └── 765 市 + 716 町 + 156 村 (prefecture:{pref}:{municipality})
    = 1,680 path-based DIDs (registerOrgTree heartbeat 自動登録)
```

### DID 確認方法

| 方法 | エンドポイント |
|---|---|
| アプリ内 | `list-dids` command → `kotodama.DIDList()` |
| XRPC | `GET /xrpc/com.atproto.identity.resolveHandle?handle=gov-jpn.etzhayyim.com` |
| DID Document | `GET https://gov-jpn.etzhayyim.com/.well-known/did.json` |
| yoro UI | `yoro.etzhayyim.com/profile/did:web:gov-jpn.etzhayyim.com:prefecture:tokyo:shibuya` |
| Kysely | `createKyselyDb().selectFrom("vertex_did").select(["did", "path"]).where("status", "=", "active").execute()` |

## India (IND) 構造

### Contract Mapping

| Contract (Law) | APP pattern | Entity DOs |
|---|---|---|
| Constitution Art. 245-263 + Individual ministry acts | individual APP per ministry | — |
| States Reorganisation Act 1956 | 1 APP: `gov-ind-state` | 28 states |
| UT Acts (various) | 1 APP: `gov-ind-ut` | 8 UTs |
| State laws (district admin) | 1 APP: `gov-ind-district` | ~770 districts |
| 73rd Amendment (Panchayati Raj) | future: panchayat APP | — |
| 74th Amendment (Municipal) | future: municipality APP | — |

### Organization Tree

```
India (ind)
├── PMO — individual APP
├── Ministry of Defence — individual APP
├── Ministry of External Affairs — individual APP
├── Ministry of Finance — individual APP
├── Ministry of Home Affairs — individual APP
├── Lok Sabha — individual APP
├── Rajya Sabha — individual APP
├── Supreme Court — individual APP
├── CAG, CBI, Election Commission, RBI ...
├── States (gov-ind-state) — 1 APP + 28 Entity DOs
│   (same contract: States Reorganisation Act)
├── Union Territories (gov-ind-ut) — 1 APP + 8 Entity DOs
│   (same contract: UT Acts)
└── Districts (gov-ind-district) — 1 APP + ~770 Entity DOs
    (under state jurisdiction)
```

## USA 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Individual enabling acts | individual APP per department | — |
| US Constitution Art. IV | 1 APP: `gov-usa-state` | 50 states |
| State law | 1 APP: `gov-usa-county` | ~3,000 counties |

### Organization Tree

```
USA (usa)
├── White House — individual APP
├── Department of Defense — individual APP
├── Department of State — individual APP
├── Department of Treasury — individual APP
├── Department of Justice — individual APP
├── FBI — individual APP
├── Supreme Court — individual APP
├── House / Senate — individual APPs
├── GAO — individual APP
├── States (gov-usa-state) — 1 APP + 50 Entity DOs
└── Counties (gov-usa-county) — 1 APP + ~3,000 Entity DOs
```

## Germany (DEU) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Grundgesetz Art. 30/70-74 + Landesverfassungen | 1 APP: `gov-deu-land` | 16 Länder |
| Grundgesetz Art. 28 + Kreisordnungen | 1 APP: `gov-deu-kreis` | ~400 Kreise |
| Individual Geschäftsordnung per ministry | individual APP per ministry | — |

### Organization Tree

```
Germany (deu)
├── Bundeskanzleramt (executive) — individual APP
├── BMVg (defense) — individual APP
├── BMF (finance) — individual APP
├── Auswärtiges Amt (foreign) — individual APP
├── BMJ (justice) — individual APP
├── Länder (gov-deu-land) — 1 APP + 16 Entity DOs
│   (Grundgesetz + each Land's Landesverfassung)
└── Kreise (gov-deu-kreis) — 1 APP + ~400 Entity DOs
    (Grundgesetz Art. 28 + Kreisordnung)
```

## France (FRA) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| CGCT Livre II (Régions) | 1 APP: `gov-fra-region` | 18 Régions |
| CGCT Livre III (Départements) | 1 APP: `gov-fra-dept` | 101 Départements |
| Individual ministry decrees | individual APP per ministry | — |

### Organization Tree

```
France (fra)
├── Présidence de la République (executive) — individual APP
├── Ministère des Armées (defense) — individual APP
├── Ministère de l'Économie (finance) — individual APP
├── Ministère des Affaires étrangères (foreign) — individual APP
├── Ministère de la Justice (justice) — individual APP
├── Régions (gov-fra-region) — 1 APP + 18 Entity DOs
│   (CGCT Livre II — same contract)
└── Départements (gov-fra-dept) — 1 APP + 101 Entity DOs
    (CGCT Livre III — same contract)
```

## United Kingdom (GBR) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Scotland Act 1998 | **separate APP**: `gov-gbr-scotland` | Scottish councils |
| Government of Wales Act 2006 | **separate APP**: `gov-gbr-wales` | Welsh councils |
| Northern Ireland Act 1998 | **separate APP**: `gov-gbr-ni` | NI councils |
| Local Government Act 1972/2000 | 1 APP: `gov-gbr-council` | ~400 councils |
| Individual enabling acts | individual APP per department | — |

### Organization Tree

```
United Kingdom (gbr)
├── HM Government (executive) — individual APP
├── Ministry of Defence (defense) — individual APP
├── HM Treasury (finance) — individual APP
├── FCDO (foreign) — individual APP
├── Ministry of Justice (justice) — individual APP
├── Scottish Parliament — **separate APP** (Scotland Act 1998)
├── Welsh Senedd — **separate APP** (Government of Wales Act 2006)
├── NI Assembly — **separate APP** (Northern Ireland Act 1998)
└── Local Councils (gov-gbr-council) — 1 APP + Entity DOs
    (Local Government Act 1972/2000)
```

## South Korea (KOR) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| 지방자치법 (Local Autonomy Act) — 광역 | 1 APP: `gov-kor-gwangyeok` | 17 광역자치단체 |
| 지방자치법 (Local Autonomy Act) — 기초 | 1 APP: `gov-kor-gicho` | 226 기초자치단체 |
| 정부조직법 (Government Organization Act) | individual APP per ministry | — |

### Organization Tree

```
South Korea (kor)
├── 대통령실 (executive) — individual APP
├── 국방부 (defense) — individual APP
├── 기획재정부 (finance) — individual APP
├── 외교부 (foreign) — individual APP
├── 법무부 (justice) — individual APP
├── 광역자치단체 (gov-kor-gwangyeok) — 1 APP + 17 Entity DOs
│   (지방자치법 — same contract)
└── 기초자치단체 (gov-kor-gicho) — 1 APP + 226 Entity DOs
    (지방자치법 — same contract)
```

## Brazil (BRA) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Constituição Federal Art. 25-28 | 1 APP: `gov-bra-estado` | 27 (26 Estados + DF) |
| Constituição Federal Art. 29-31 | 1 APP: `gov-bra-municipio` | 5,570 Municípios |
| Individual ministry enabling laws | individual APP per ministry | — |

### Organization Tree

```
Brazil (bra)
├── Presidência da República (executive) — individual APP
├── Ministério da Defesa (defense) — individual APP
├── Ministério da Fazenda (finance) — individual APP
├── Itamaraty (foreign) — individual APP
├── Ministério da Justiça (justice) — individual APP
├── Estados (gov-bra-estado) — 1 APP + 27 Entity DOs
│   (Constituição Federal + Constituições Estaduais)
└── Municípios (gov-bra-municipio) — 1 APP + 5,570 Entity DOs
    (Constituição Federal Art. 29-31 + Lei Orgânica)
```

## Canada (CAN) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Constitution Act 1867 s.91-95 + 1982 | 1 APP: `gov-can-province` | 13 (10 provinces + 3 territories) |

### Organization Tree

```
Canada (can)
├── PMO (executive) — individual APP
├── DND (defense) — individual APP
├── Global Affairs (foreign) — individual APP
├── Finance (finance) — individual APP
├── Justice (justice) — individual APP
├── Provinces/Territories (gov-can-province) — 1 APP + 13 Entity DOs
│   (Constitution Act 1867/1982 — same framework)
│   Territories have delegated (not inherent) powers but same APP
└── [future: municipalities per province]
```

## Italy (ITA) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Costituzione Art. 114-133 | 1 APP: `gov-ita-regione` | 20 regioni |

### Organization Tree

```
Italy (ita)
├── Presidenza del Consiglio (executive) — individual APP
├── Ministero della Difesa (defense) — individual APP
├── MEF (finance) — individual APP
├── MAECI (foreign) — individual APP
├── Ministero della Giustizia (justice) — individual APP
├── Regioni (gov-ita-regione) — 1 APP + 20 Entity DOs
│   (Costituzione Art. 114-133 — same framework)
│   5 statuto speciale (Sicilia, Sardegna, TAA, FVG, VdA) = same constitutional root
└── [future: province, comuni]
```

## Spain (ESP) 構造

### Contract Mapping & Analysis

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Constitution 1978 Title VIII + 17 Estatutos | 1 APP: `gov-esp-comunidad` | 19 (17 comunidades + 2 ciudades) |

**Contract analysis**: All 17 Statutes of Autonomy derive from Constitution Art. 143-152.
Unlike GBR devolution (separate Acts of Parliament), Spanish autonomy is a single constitutional
framework. All Statutes are approved as Ley Organica by Cortes Generales.
Foral territories (Navarra: LORAFNA, Pais Vasco: Concierto Economico) have fiscal autonomy
but within same constitutional framework → **1 APP**, not 17 separate APPs.

```
Spain (esp)
├── Presidencia del Gobierno (executive) — individual APP
├── Ministerio de Defensa (defense) — individual APP
├── Ministerio de Hacienda (finance) — individual APP
├── MAEC (foreign) — individual APP
├── Ministerio de Justicia (justice) — individual APP
├── Comunidades Autonomas (gov-esp-comunidad) — 1 APP + 19 Entity DOs
│   (Constitution 1978 + Estatutos de Autonomia — single framework)
└── [future: provincias, municipios]
```

## Netherlands (NLD) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Grondwet + Provinciewet + WolBES | 1 APP: `gov-nld-provincie` | 15 (12 provincies + 3 BES) |

BES islands (Bonaire, Sint Eustatius, Saba) under WolBES = different law but still Dutch
constitutional framework (Grondwet Art. 132a) → modeled as Entity DOs within same APP.
Aruba, Curacao, Sint Maarten are separate countries within Kingdom → separate APPs if needed.

```
Netherlands (nld)
├── Minister-President (executive) — individual APP
├── Ministerie van Defensie (defense) — individual APP
├── Ministerie van Financien (finance) — individual APP
├── Ministerie van Buitenlandse Zaken (foreign) — individual APP
├── Ministerie van J&V (justice) — individual APP
├── Provincies + BES (gov-nld-provincie) — 1 APP + 15 Entity DOs
│   (Grondwet + Provinciewet / WolBES — same constitutional framework)
└── [future: gemeenten]
```

## Belgium (BEL) 構造

### Contract Mapping & Analysis

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Grondwet Art. 1-5 + Bijzondere Wetten | 1 APP: `gov-bel-region` | 6 (3 Regions + 3 Communities) |

**Contract analysis**: Despite extreme complexity (3 Regions + 3 Communities with overlapping
territorial jurisdiction), all 6 entities derive from same Belgian Constitution Art. 1-5.
Bijzondere Wetten (Special Majority Laws, e.g., BWHI 8 Aug 1980) implement the division
but are NOT separate contracts like GBR devolution Acts. The constitutional root is single.
Flemish Community and Region merged institutions but remain legally distinct → 2 Entity DOs.

```
Belgium (bel)
├── Premier ministre (executive) — individual APP
├── Ministere de la Defense (defense) — individual APP
├── SPF Finances (finance) — individual APP
├── SPF Affaires etrangeres (foreign) — individual APP
├── SPF Justice (justice) — individual APP
├── Regions & Communities (gov-bel-region) — 1 APP + 6 Entity DOs
│   ├── Vlaams Gewest (Flemish Region)
│   ├── Region wallonne (Walloon Region)
│   ├── Region de Bruxelles-Capitale (Brussels-Capital Region)
│   ├── Vlaamse Gemeenschap (Flemish Community)
│   ├── Communaute francaise (French Community)
│   └── Deutschsprachige Gemeinschaft (German-speaking Community)
│   (Grondwet Art. 1-5 — single constitutional framework)
└── [future: provinces, communes/gemeenten]
```

## Switzerland (CHE) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Bundesverfassung 1999 Art. 3/42-53 | 1 APP: `gov-che-kanton` | 26 Kantone |

```
Switzerland (che)
├── Bundesrat (7-member directorial council) — individual APP
├── VBS/DDPS (defense) — individual APP
├── EFD/DFF (finance) — individual APP
├── EDA/DFAE (foreign) — individual APP
├── EJPD/DFJP (justice) — individual APP
├── Kantone (gov-che-kanton) — 1 APP + 26 Entity DOs
│   (Bundesverfassung + Kantonsverfassungen — same federal framework)
└── [future: Gemeinden]
```

## Austria (AUT) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| B-VG 1920 Art. 2/10-15 | 1 APP: `gov-aut-bundesland` | 9 Bundeslaender |

```
Austria (aut)
├── Bundeskanzleramt (executive) — individual APP
├── BMLV (defense) — individual APP
├── BMF (finance) — individual APP
├── BMEIA (foreign) — individual APP
├── BMJ (justice) — individual APP
├── Bundeslaender (gov-aut-bundesland) — 1 APP + 9 Entity DOs
│   (B-VG + Landesverfassungen — same framework)
│   Note: constitutionally neutral, NOT NATO member
└── [future: Bezirke]
```

## Poland (POL) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Konstytucja Art. 163-172 + Ustawa o samorzadzie | 1 APP: `gov-pol-wojewodztwo` | 16 wojewodztw |

```
Poland (pol)
├── Kancelaria PRM (executive) — individual APP
├── MON (defense) — individual APP
├── MF (finance) — individual APP
├── MSZ (foreign) — individual APP
├── MS (justice) — individual APP
├── Wojewodztwa (gov-pol-wojewodztwo) — 1 APP + 16 Entity DOs
│   (Konstytucja + Ustawa o samorzadzie — same framework)
│   Dual admin: elected marszalek + appointed wojewoda
└── [future: powiaty, gminy]
```

## Sweden (SWE) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Regeringsformen Ch. 14 + Kommunallagen | 1 APP: `gov-swe-lan` | 21 lan/regioner |

```
Sweden (swe)
├── Statsradsberedningen (executive) — individual APP
├── Forsvarsdepartementet (defense) — individual APP
├── Finansdepartementet (finance) — individual APP
├── Utrikesdepartementet (foreign) — individual APP
├── Justitiedepartementet (justice) — individual APP
├── Lan/Regioner (gov-swe-lan) — 1 APP + 21 Entity DOs
│   (Regeringsformen + Kommunallagen — same framework)
└── [future: kommuner]
```

## Norway (NOR) 構造

### Contract Mapping

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Grunnloven + kommuneloven | 1 APP: `gov-nor-fylke` | 11 fylker |

```
Norway (nor)
├── Statsministerens kontor (executive) — individual APP
├── Forsvarsdepartementet (defense) — individual APP
├── Finansdepartementet (finance) — individual APP
├── Utenriksdepartementet (foreign) — individual APP
├── JD (justice) — individual APP
├── Fylker (gov-nor-fylke) — 1 APP + 11 Entity DOs
│   (Grunnloven + kommuneloven — same framework)
│   Note: NOT EU member (EEA/EFTA)
└── [future: kommuner]
```

## Denmark (DNK) 構造

### Contract Mapping & Analysis

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Grundloven + Regionsloven | 1 APP: `gov-dnk-region` | 5 regioner (mainland) |
| Selvstyreloven 2009 | **separate APP**: `gov-dnk-greenland` | Greenland municipalities |
| Hjemmestyreloven 1948 + Overtagelsesloven 2005 | **separate APP**: `gov-dnk-faroe` | Faroese municipalities |

**Contract analysis**: Greenland and Faroe Islands have SEPARATE legal contracts distinct
from Danish Grundloven. Selvstyreloven 2009 grants Greenland right to self-determination.
Hjemmestyreloven 1948 + Overtagelsesloven 2005 grant Faroe progressive competence takeover.
Both opted out of EU. These are genuinely different contracts → **3 separate APPs**.

```
Denmark (dnk)
├── Statsministeriet (executive) — individual APP
├── Forsvarsministeriet (defense) — individual APP
├── Finansministeriet (finance) — individual APP
├── Udenrigsministeriet (foreign) — individual APP
├── Justitsministeriet (justice) — individual APP
├── Regioner (gov-dnk-region) — 1 APP + 5 Entity DOs
│   (Grundloven + Regionsloven — mainland only)
├── Greenland (gov-dnk-greenland) — **SEPARATE APP**
│   (Selvstyreloven 2009 — different contract, self-determination)
└── Faroe Islands (gov-dnk-faroe) — **SEPARATE APP**
    (Hjemmestyreloven 1948 + Overtagelsesloven 2005 — different contract)
```

## Finland (FIN) 構造

### Contract Mapping & Analysis

| Contract | APP pattern | Entity DOs |
|---|---|---|
| Perustuslaki + Maakuntalaki | 1 APP: `gov-fin-maakunta` | 18 maakunnat (mainland) |
| Ahvenanmaan itsehallintolaki 1991 | **separate APP**: `gov-fin-aland` | Aland municipalities |

**Contract analysis**: Aland Autonomy Act 1991 is a genuinely separate legal contract from
Finnish Maakuntalaki. Aland has own parliament (Lagting), government, demilitarized status
(1856 Paris Treaty), Swedish-speaking, own tax regime, EU special protocol.
This is a different contract → **2 separate APPs**.

```
Finland (fin)
├── Valtioneuvoston kanslia (executive) — individual APP
├── Puolustusministerio (defense) — individual APP
├── Valtiovarainministerio (finance) — individual APP
├── Ulkoministerio (foreign) — individual APP
├── Oikeusministerio (justice) — individual APP
├── Maakunnat (gov-fin-maakunta) — 1 APP + 18 Entity DOs
│   (Perustuslaki + Maakuntalaki — mainland only)
│   Regions are joint municipal authorities (kuntayhtymia)
└── Aland (gov-fin-aland) — **SEPARATE APP**
    (Ahvenanmaan itsehallintolaki 1991 — different contract, demilitarized)
```

## Middle East 構造

### Contract Mapping

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **SAU** | Basic Law 1992 (Royal Decree A/90) | 1 APP: `gov-sau-mintaqah` | 13 mintaqah | Absolute monarchy, Amir-appointed governors |
| **ARE** | Constitution 1971 | 1 APP: `gov-are-emirate` | 7 emirates | Federal, each emirate retains sovereignty over non-federal matters |
| **QAT** | Constitution 2004 | 1 APP: `gov-qat-baladiyah` | 8 baladiyat | Absolute monarchy (Emir) |
| **KWT** | Constitution 1962 | 1 APP: `gov-kwt-muhafazah` | 6 muhafazat | Constitutional monarchy + elected National Assembly |
| **BHR** | Constitution 2002 | 1 APP: `gov-bhr-muhafazah` | 4 muhafazat | Constitutional monarchy + bicameral parliament |
| **OMN** | Basic Law 1996 (RD 101/96) | 1 APP: `gov-omn-muhafazah` | 11 muhafazat | Absolute monarchy (Sultan) |
| **JOR** | Constitution 1952 | 1 APP: `gov-jor-muhafazah` | 12 muhafazat | Constitutional monarchy, Decentralization Law 2015 |
| **LBN** | Constitution 1926/Taif 1990 | 1 APP: `gov-lbn-muhafazah` | 8 muhafazat | Confessional republic (unique: President=Maronite, PM=Sunni, Speaker=Shia) |
| **YEM** | Constitution 1991 | 1 APP: `gov-yem-muhafazah` | 22 muhafazat | Republic (civil war: Houthi north / STC south / intl-recognized gov) |

## Central Asia 構造

### Contract Mapping

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **AFG** | Constitution 2004 (contested) | 1 APP: `gov-afg-wilayat` | 34 wilayat | Islamic republic, post-2021 Taliban interim outside constitutional framework |
| **PAK** | Constitution 1973 (18th Amdt 2010) | 1 APP: `gov-pak-province` | 7 (4 provinces + ICT + AJK + GB) | Federal, provinces share constitutional framework. FATA merged into KPK (25th Amdt 2018) |
| **KAZ** | Constitution 1995 | 1 APP: `gov-kaz-oblys` | 20 (17 oblystary + 3 cities) | Unitary presidential, akims appointed by President |
| **UZB** | Constitution 1992 | 1 APP: `gov-uzb-viloyat` | 12 viloyatlar + Tashkent city | Unitary presidential. **Karakalpakstan = separate APP** (Art. 70-75, own constitution) |
| **UZB-KK** | Karakalpakstan Constitution (UZB Art. 70-75) | **separate APP**: `gov-uzb-karakalpakstan` | 1 autonomous republic | Autonomous republic within Uzbekistan with own constitution |
| **TKM** | Constitution 2008 | 1 APP: `gov-tkm-welayat` | 5 welayatlar | Unitary presidential |
| **KGZ** | Constitution 2021 | 1 APP: `gov-kgz-oblast` | 7 oblasttar | Unitary parliamentary (shifted from parliamentary to presidential 2021) |

## Sub-Saharan Africa 構造

### Contract Boundary Analysis

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **ZAF** | Constitution 1996, Schedules 4-5 | 1 APP: `gov-zaf-province` | 9 provinces | Federal-like, provincial legislatures |
| **KEN** | Constitution 2010 Ch.11 + County Government Act 2012 | 1 APP: `gov-ken-county` | 47 counties | Devolved unitary |
| **ETH** | Constitution 1995 Art. 47 | 1 APP: `gov-eth-region` | 12 regional states + 2 chartered cities (14) | Ethnic federalism, regions have own constitutions but under same Art. 47 |
| **TZA (Union)** | Union Constitution 1977 | 1 APP: `gov-tza-mkoa` | 31 mikoa | Zanzibar is **separate APP** |
| **TZA (Zanzibar)** | Zanzibar Constitution 1984 | **separate APP**: `gov-tza-zanzibar` | 5 regions | Different constitutional arrangement |
| **GHA** | Constitution 1992 Ch.20 | 1 APP: `gov-gha-region` | 16 regions | Unitary |
| **CMR** | Constitution 1972/1996 Title X | 1 APP: `gov-cmr-region` | 10 regions | Anglophone NW/SW under same legal framework |
| **SEN** | Constitution 2001 Title XI | 1 APP: `gov-sen-region` | 14 regions | Unitary |
| **CIV** | Constitution 2016 Title XII | 1 APP: `gov-civ-region` | 31 regions + 2 districts autonomes (33) | Unitary |
| **MDG** | Constitution 2010 Title VI | 1 APP: `gov-mdg-faritra` | 22 faritra | Unitary |
| **MOZ** | Constitution 2004 Title XIV | 1 APP: `gov-moz-provincia` | 10 provincias + Maputo (11) | Unitary |
| **AGO** | Constitution 2010 Title VI | 1 APP: `gov-ago-provincia` | 18 provincias | Unitary presidential |
| **ZWE** | Constitution 2013 Ch.14 | 1 APP: `gov-zwe-province` | 10 provinces | Unitary |
| **RWA** | Constitution 2003 (amended 2015) | 1 APP: `gov-rwa-intara` | 5 intara | Unitary |
| **UGA** | Constitution 1995 Ch.11 + Local Governments Act 1997 | 1 APP: `gov-uga-district` | 135+ districts | Cultural kingdoms = not separate contracts |
| **COD** | Constitution 2006 Title III | 1 APP: `gov-cod-province` | 26 provinces | Federal-like, provincial assemblies |

**Total**: 15 countries → **16 APPs** (TZA split: Union + Zanzibar)

### Key Contract Boundary Decisions

- **TZA**: Zanzibar Constitution 1984 is a separate legal instrument from the Union Constitution 1977 → **separate APP**
- **ETH**: Regions have own constitutions but all enumerated under Federal Art. 47 → **same APP** with 14 Entity DOs
- **UGA**: Kingdom regions (Buganda, Bunyoro, etc.) have cultural autonomy only, not governance contracts → **not separate contracts**
- **CMR**: Anglophone regions (NW/SW) have decentralization grievances but legally same Title X framework → **same APP**

## Latin America 構造

### Contract Mapping

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **ARG** | Constitución 1994 Art. 121-129 | 1 APP: `gov-arg-provincia` | 24 (23 provincias + CABA) | Federal, provincial constitutions, CABA Art. 129 |
| **BOL** | Constitution 2009 Art. 269-276 | 1 APP: `gov-bol-departamento` | 9 departamentos | Plurinational State, indigenous autonomies |
| **CHL** | Constitution 1980/2005 + Ley 19.175 | 1 APP: `gov-chl-region` | 16 regiones | Elected Gobernador since 2021 |
| **CRI** | Constitution 1949 Art. 168-175 | 1 APP: `gov-cri-provincia` | 7 provincias | No standing army (abolished 1948) |
| **DOM** | Constitution 2010 Art. 196-200 | 1 APP: `gov-dom-provincia` | 32 provincias | Appointed governors, administrative |
| **ECU** | Constitution 2008 Art. 252-258 + COOTAD | 1 APP: `gov-ecu-provincia` | 24 provincias | Mandatory decentralization |
| **GTM** | Constitution 1985 Art. 224-231 | 1 APP: `gov-gtm-departamento` | 22 departamentos | Appointed governors |
| **GUY** | Constitution 1980 Art. 72-78 | 1 APP: `gov-guy-region` | 10 regions | Co-operative Republic, elected RDC |
| **HND** | Constitution 1982 Art. 294-302 | 1 APP: `gov-hnd-departamento` | 18 departamentos | Appointed governors |
| **HTI** | Constitution 1987 Art. 75-87.5 | 1 APP: `gov-hti-departement` | 10 departements | Governance instability |
| **JAM** | Constitution 1962 + Parish Councils Act | 1 APP: `gov-jam-parish` | 14 parishes | Constitutional Monarchy (Commonwealth) |
| **NIC** | Constitution 1987 Art. 175-181 + Ley 28 | 1 APP: `gov-nic-departamento` | 17 (15 dept + 2 autonomous regions) | Atlantic Coast autonomy (RACCN/RACCS) |
| **PAN** | Constitution 1972/2004 Art. 5 | 1 APP: `gov-pan-provincia` | 15 (10 prov + 5 comarcas) | No military since 1990, indigenous comarcas |
| **PER** | Constitution 1993 + Ley 27867 | 1 APP: `gov-per-departamento` | 25 departamentos | Elected Gobernador Regional |
| **PRY** | Constitution 1992 Art. 161-171 | 1 APP: `gov-pry-departamento` | 18 (17 dept + Asuncion) | Elected Gobernador + Junta |
| **SLV** | Constitution 1983 Art. 200-207 | 1 APP: `gov-slv-departamento` | 14 departamentos | Appointed governors |
| **SUR** | Constitution 1987 Art. 160-166 | 1 APP: `gov-sur-district` | 10 districten | Appointed + elected Districtsraad |
| **URY** | Constitution 1967 Art. 262-288 | 1 APP: `gov-ury-departamento` | 19 departamentos | Elected Intendente + Junta |
| **VEN** | Constitution 1999 Art. 159-167 | 1 APP: `gov-ven-estado` | 23 estados | Federal but Chavez-era centralization |

**Total**: 19 countries → **19 APPs**

### Key Contract Boundary Decisions

- **ARG**: Federal with strong provincial autonomy. CABA has special Art. 129 status but same constitutional root → Entity DO within same APP
- **VEN**: Nominally federal but Poder Popular reduced state autonomy de facto → 1 APP (unified framework)
- **NIC**: RACCN/RACCS have Ley 28 autonomy but derive from same Constitution Art. 175-181 → Entity DOs in same APP
- **PAN**: Comarcas indígenas (Guna Yala, Emberá-Wounaan, Ngäbe-Buglé) have semi-autonomous status under same Constitution Art. 5 → Entity DOs

## Europe Remaining 構造

### Contract Mapping

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **UKR** | Constitution 1996 Art. 132-144 | 1 APP: `gov-ukr-oblast` | 27 (24 oblasts + Crimea AR + Kyiv + Sevastopol) | Crimea under Russian occupation since 2014 |
| **GRC** | Constitution 1975 Art. 101-102 + Kallikratis 3852/2010 | 1 APP: `gov-grc-periphereia` | 14 (13 regions + Mount Athos) | Mount Athos Art. 105 monastic self-government |
| **CZE** | Constitution 1993 Art. 99-105 + Act 129/2000 | 1 APP: `gov-cze-kraj` | 14 (13 regions + Prague) | V4 Group |
| **HUN** | Fundamental Law 2011 Art. 31-35 | 1 APP: `gov-hun-megye` | 20 (19 megyek + Budapest) | V4 Group |
| **ROU** | Constitution 1991/2003 Art. 120-123 | 1 APP: `gov-rou-judet` | 42 (41 judete + Bucuresti) | Largest Entity DO count in Europe |
| **BGR** | Constitution 1991 Art. 135-146 | 1 APP: `gov-bgr-oblast` | 28 oblasti | Appointed governors |
| **HRV** | Constitution 1990 Art. 133-138 | 1 APP: `gov-hrv-zupanija` | 21 (20 zupanije + Zagreb) | EU 2013 |
| **SRB** | Constitution 2006 Art. 176-193 | 1 APP: `gov-srb-okrug` | 27 (25 okruzi + AP Vojvodina + AP Kosovo) | Vojvodina enhanced autonomy as Entity DO |
| **SVK** | Constitution 1992 Art. 64a + Act 302/2001 | 1 APP: `gov-svk-kraj` | 8 kraje | V4 Group |
| **SVN** | Constitution 1991 Art. 143 | 1 APP: `gov-svn-regija` | 12 statistical regions | No elected regional government |
| **ALB** | Constitution 1998 Art. 108-115 | 1 APP: `gov-alb-qark` | 12 qarqe | NATO 2009, EU candidate |
| **BIH** | Dayton 1995 Annex 4 | **3 APPs** | RS + FBiH(10 cantons) + Brcko | Genuinely separate constitutions |
| **MKD** | Constitution 1991 Art. 114-117 + Ohrid 2001 | 1 APP: `gov-mkd-region` | 8 statistical regions | NATO 2020 |
| **MNE** | Constitution 2007 Art. 113-117 | 1 APP: `gov-mne-opstina` | 25 opstine | NATO 2017 |
| **GEO** | Constitution 1995 Art. 7 | 1 APP: `gov-geo-mkhare` | 12 (9 regions + Tbilisi + Adjara + Abkhazia) | Abkhazia/S.Ossetia Russian-occupied |
| **EST** | Constitution 1992 Ch. XIV | 1 APP: `gov-est-maakond` | 15 maakonnad | County admin abolished 2017 |
| **LTU** | Constitution 1992 Art. 119-124 | 1 APP: `gov-ltu-apskritis` | 10 apskritys | County admin abolished 2010 |
| **LVA** | Constitution Art. 101 + Law 2020 | 1 APP: `gov-lva-novads` | 5 planning regions | 2021 reform consolidated |
| **ISL** | Constitution 1944 Art. 78 | 1 APP: `gov-isl-landshluti` | 8 statistical regions | EEA/EFTA not EU |
| **LUX** | Constitution 1868 Art. 107-108 | 1 APP: `gov-lux-canton` | 12 cantons | EU/NATO founding member |
| **PRT** | Constitution 1976 Art. 225-262 | 1 APP: `gov-prt-distrito` | 20 (18 distritos + Acores + Madeira) | ARs under same constitutional root |
| **CYP** | Constitution 1960 Art. 173-178 | 1 APP: `gov-cyp-eparchia` | 6 districts | Northern districts under TRNC de facto |

**Total**: 22 countries → **25 APPs** (BIH = 3)

### Key Contract Boundary Decisions

- **BIH**: Republika Srpska Constitution, Federation BiH Constitution, Brcko Statute are genuinely separate legal instruments (Dayton Agreement) → **3 APPs**
- **SRB**: Vojvodina has Statute of Autonomy 2014 with own Assembly and Government, BUT derives from same Constitution Art. 182-187 → **1 APP**, Vojvodina as enhanced Entity DO
- **PRT**: Acores (Estatuto 1980/2009) and Madeira (Estatuto 1991/2000) have autonomous status BUT both derive from same Constitution Art. 225-234 → **1 APP** (unlike GBR devolution which uses separate Acts)
- **GEO**: Abkhazia and South Ossetia are de facto independent (Russian-occupied since 2008) but internationally recognized as Georgia → Entity DOs with territorial_control flag
- **CYP**: TRNC (Northern Cyprus) recognized only by Turkey; Republic of Cyprus Constitution 1960 covers whole island → **1 APP**, northern districts flagged
- **UKR**: Crimea AR under Russian occupation since 2014 but internationally recognized as Ukraine → Entity DO within same APP

## Missing Countries (9)

| Country | Contract | APP pattern | Entity DOs | Key |
|---|---|---|---|---|
| **AND** | Constitution 1993 Art. 79-84 | 1 APP: `gov-and-parroquia` | 7 parroquies | Co-principality (Bishop of Urgell + President of France) |
| **ATG** | Constitution 1981 | 1 APP: `gov-atg-national` | 0 (tiny state) | CARICOM, ~100k pop |
| **BRB** | Constitution 1966/2021 | 1 APP: `gov-brb-national` | 0 (tiny state) | Republic since 2021 |
| **DMA** | Constitution 1978 | 1 APP: `gov-dma-national` | 0 (tiny state) | OECS, ~72k pop |
| **GRD** | Constitution 1973 | 1 APP: `gov-grd-national` | 0 (tiny state) | CARICOM, ~113k pop |
| **LBY** | Constitutional Declaration 2011 | 1 APP: `gov-lby-shabiyah` | 22 shabiyat | Civil war, contested governance |
| **MHL** | Constitution 1979 + Compact | 1 APP: `gov-mhl-national` | 0 (micro state) | Compact of Free Association with USA |
| **MLT** | Constitution 1964 Art. 115A | 1 APP: `gov-mlt-regjun` | 5 regions | EU 2004, ~520k pop |

**Total**: 8 unique countries → **8 APPs** (MNE already counted in Europe)

## Resource Flow (ヒトモノカネ)

`etzhayyim:gov-resource-flow@1.0.0` (`wit/gov-resource-flow/package.wit`) で全エンティティ間の資源フローを時系列追跡:

| Interface | Resource Class | 用途 |
|---|---|---|
| `personnel` | ヒト | 定員配分、人事異動、出向、個人レベル追跡 |
| `assets` | モノ | 政府調達、国有財産、物品管理、契約番号追跡 |
| `budget` | カネ | 予算配分、補助金、交付金、契約支払い |
| `resource-flow` | 統合 | 時系列、multi-hop lineage、entity 登録・検索 |

### Flow Entity — 全エンティティ追跡

flow の source/destination は政府組織に限定しない。`flow-entity` record で全種別を追跡:

| entity-kind | 例 |
|---|---|
| `gov-org` | 省庁、局、課 |
| `agency` | 独立行政法人、特殊法人 |
| `local-gov` | 都道府県、市区町村 |
| `private-corp` | 民間企業 (法人番号で紐付け) |
| `npo` | NPO法人、社団法人 |
| `association` | 業界団体、協会 |
| `individual` | 個人 (匿名化 person_id) |
| `foreign-gov` | 外国政府、大使館 |
| `international-org` | 国連、WHO 等 |

### 時系列・Lineage

- `get-flow-time-series`: 任意の source→destination 間の過去全履歴を時系列で取得
- `trace-flow-lineage`: multi-hop lineage (例: 国庫→MOF→MHLW→都道府県→市区町村→委託業者→下請→個人)
- 全 flow に `effective_date` + `fiscal_year` → 過去の任意時点に遡及可能

### Data Flow

W Protocol Event Stream (write: WRecord → PDS → yata SQL direct (SHA-256 content CID), read: Q/G) → SQL graph (analytics / Sankey / lineage traversal)

| SQL Node | 用途 |
|---|---|
| `:FlowEntity` | 全エンティティ (org, corp, individual...) のマスタ node |
| `:GovBudgetFlow` | 予算 flow event (source_id, destination_id, amount_jpy, effective_date) |
| `:GovPersonnelFlow` | 人事 flow event (headcount, grade, person_ids) |
| `:GovAssetFlow` | 資産 flow event (asset_class, asset_ref, value_jpy) |

**MOF exports**: `etzhayyim:gov-resource-flow/budget@1.0.0` + `resource-flow@1.0.0` (authoritative source)。他省庁は import。

## Capability WIT

各省庁の capability は `60-apps/etzhayyim-project-states/wit/` に配置:

```
wit/
├── gov-resource-flow/package.wit — ヒトモノカネ resource flow (personnel, assets, budget, combined)
├── gov-deu/package.wit        — land-administration, kreis-administration, executive, defense, finance, foreign, justice
├── gov-fra/package.wit        — region-administration, departement-administration, executive, defense, finance, foreign, justice
├── gov-gbr/package.wit        — scotland/wales/ni-devolution, council-administration, executive, defense, finance, foreign, justice
├── gov-kor/package.wit        — gwangyeok-administration, gicho-administration, executive, defense, finance, foreign, justice
├── gov-bra/package.wit        — estado-administration, municipio-administration, executive, defense, finance, foreign, justice
├── gov-jpn-moj/package.wit    — coordination, civil-affairs, criminal-affairs, ...
├── gov-jpn-cao/package.wit    — policy-coordination, space-policy
├── gov-jpn-mic/package.wit    — admin-management, statistics, fire-disaster
├── gov-jpn-mof/package.wit    — budget, taxation, customs, national-tax
├── gov-jpn-mext/package.wit   — education, science-technology, cultural-affairs
├── gov-jpn-mhlw/package.wit   — health-policy, labour-standards, pension
├── gov-jpn-maff/package.wit   — agriculture, forestry, fisheries
├── gov-jpn-meti/package.wit   — trade-policy, industry, energy, patents
├── gov-jpn-mlit/package.wit   — transport, urban-planning, coast-guard, meteorology
├── gov-jpn-moe/package.wit    — environment, nature-conservation
├── gov-jpn-mod/package.wit    — defense-policy, joint-operations, acquisition
├── gov-jpn-npa/package.wit    — public-safety, criminal-investigation, cyber-police
├── gov-jpn-prefecture/        — prefectural-admin
├── gov-jpn-municipality/      — municipal-admin
├── gov-can/package.wit        — province-administration, executive, defense, finance, foreign, justice
├── gov-ita/package.wit        — regione-administration, executive, defense, finance, foreign, justice
├── gov-esp/package.wit        — comunidad-administration, executive, defense, finance, foreign, justice
├── gov-nld/package.wit        — provincie-administration, executive, defense, finance, foreign, justice
├── gov-bel/package.wit        — region-community-administration, executive, defense, finance, foreign, justice
├── gov-che/package.wit        — kanton-administration, executive, defense, finance, foreign, justice
├── gov-aut/package.wit        — bundesland-administration, executive, defense, finance, foreign, justice
├── gov-pol/package.wit        — wojewodztwo-administration, executive, defense, finance, foreign, justice
├── gov-swe/package.wit        — lan-administration, executive, defense, finance, foreign, justice
├── gov-nor/package.wit        — fylke-administration, executive, defense, finance, foreign, justice
├── gov-dnk/package.wit        — region-administration, greenland-selfgovernment, faroe-homerule, executive, defense, finance, foreign, justice
├── gov-fin/package.wit        — maakunta-administration, aland-autonomy, executive, defense, finance, foreign, justice
├── gov-zaf/package.wit        — province-administration, executive, national-coordination
├── gov-ken/package.wit        — county-administration, national-coordination
├── gov-eth/package.wit        — regional-state-administration, federal-coordination
├── gov-tza/package.wit        — mkoa-administration, union-coordination, zanzibar-administration
├── gov-gha/package.wit        — region-administration, national-coordination
├── gov-cmr/package.wit        — region-administration, national-coordination
├── gov-sen/package.wit        — region-administration, national-coordination
├── gov-civ/package.wit        — region-administration, district-autonome-administration, national-coordination
├── gov-mdg/package.wit        — faritra-administration, national-coordination
├── gov-moz/package.wit        — provincia-administration, national-coordination
├── gov-ago/package.wit        — provincia-administration, national-coordination
├── gov-zwe/package.wit        — province-administration, national-coordination
├── gov-rwa/package.wit        — intara-administration, national-coordination
├── gov-uga/package.wit        — district-administration, national-coordination
├── gov-cod/package.wit        — province-administration, national-coordination
├── gov-sau/package.wit        — mintaqah-administration, executive, defense, finance, foreign, justice, interior
├── gov-are/package.wit        — emirate-administration, federal-coordination, executive, defense, finance, foreign, justice
├── gov-qat/package.wit        — baladiyah-administration, executive, defense, finance, foreign, justice
├── gov-kwt/package.wit        — muhafazah-administration, executive, defense, finance, foreign, justice
├── gov-bhr/package.wit        — muhafazah-administration, executive, defense, finance, foreign, justice
├── gov-omn/package.wit        — muhafazah-administration, executive, defense, finance, foreign, justice
├── gov-jor/package.wit        — muhafazah-administration, executive, defense, finance, foreign, justice
├── gov-lbn/package.wit        — muhafazah-administration, confessional-governance, executive, defense, finance, foreign, justice
├── gov-yem/package.wit        — muhafazah-administration, executive, defense, finance, foreign, justice
├── gov-afg/package.wit        — wilayat-administration, executive, defense, finance, foreign, justice
├── gov-pak/package.wit        — province-administration, federal-coordination, executive, defense, finance, foreign, justice
├── gov-kaz/package.wit        — oblys-administration, executive, defense, finance, foreign, justice
├── gov-uzb/package.wit        — viloyat-administration, karakalpakstan-autonomy, executive, defense, finance, foreign, justice
├── gov-tkm/package.wit        — welayat-administration, executive, defense, finance, foreign, justice
├── gov-kgz/package.wit        — oblast-administration, executive, defense, finance, foreign, justice
├── gov-ind/package.wit        — union-coordination, state-administration, ...
├── gov-arg/package.wit        — provincia-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-bol/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-chl/package.wit        — region-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-cri/package.wit        — provincia-administration, national-coordination, finance, foreign-affairs, justice
├── gov-dom/package.wit        — provincia-administration, national-coordination, defense, finance, foreign-affairs
├── gov-ecu/package.wit        — provincia-administration, national-coordination, defense, finance, foreign-affairs
├── gov-gtm/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-guy/package.wit        — region-administration, national-coordination, defense, finance, foreign-affairs
├── gov-hnd/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-hti/package.wit        — departement-administration, national-coordination, defense, finance, foreign-affairs
├── gov-jam/package.wit        — parish-administration, national-coordination, defense, finance, foreign-affairs
├── gov-nic/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-pan/package.wit        — provincia-administration, national-coordination, public-security, finance, foreign-affairs
├── gov-per/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-pry/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-slv/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-sur/package.wit        — district-administration, national-coordination, defense, finance, foreign-affairs
├── gov-ury/package.wit        — departamento-administration, national-coordination, defense, finance, foreign-affairs
├── gov-ven/package.wit        — estado-administration, national-coordination, defense, finance, foreign-affairs
├── gov-ukr/package.wit        — oblast-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-grc/package.wit        — periphereia-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-cze/package.wit        — kraj-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-hun/package.wit        — megye-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-rou/package.wit        — judet-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-bgr/package.wit        — oblast-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-hrv/package.wit        — zupanija-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-srb/package.wit        — okrug-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-svk/package.wit        — kraj-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-svn/package.wit        — regija-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-alb/package.wit        — qark-administration, national-coordination, defense, finance, foreign-affairs
├── gov-bih/package.wit        — republika-srpska-administration, federation-bih-administration, brcko-administration, state-coordination, defense, finance, foreign-affairs
├── gov-mkd/package.wit        — region-administration, national-coordination, defense, finance, foreign-affairs
├── gov-mne/package.wit        — opstina-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-geo/package.wit        — mkhare-administration, national-coordination, defense, finance, foreign-affairs
├── gov-est/package.wit        — maakond-administration, national-coordination, defense, finance, foreign-affairs
├── gov-ltu/package.wit        — apskritis-administration, national-coordination, defense, finance, foreign-affairs
├── gov-lva/package.wit        — novads-administration, national-coordination, defense, finance, foreign-affairs
├── gov-isl/package.wit        — landshluti-administration, national-coordination, finance, foreign-affairs
├── gov-lux/package.wit        — canton-administration, national-coordination, defense, finance, foreign-affairs
├── gov-prt/package.wit        — distrito-administration, national-coordination, defense, finance, foreign-affairs, justice
├── gov-cyp/package.wit        — eparchia-administration, national-coordination, defense, finance, foreign-affairs
├── gov-and/package.wit        — parroquia-administration, national-coordination, finance, foreign-affairs
├── gov-atg/package.wit        — national-coordination, finance, foreign-affairs
├── gov-brb/package.wit        — national-coordination, defense, finance, foreign-affairs
├── gov-dma/package.wit        — national-coordination, finance, foreign-affairs
├── gov-grd/package.wit        — national-coordination, finance, foreign-affairs
├── gov-lby/package.wit        — shabiyah-administration, national-coordination, defense, finance, foreign-affairs
├── gov-mhl/package.wit        — national-coordination, finance, foreign-affairs
└── gov-mlt/package.wit        — regjun-administration, national-coordination, defense, finance, foreign-affairs
```

## world.wit 必須構造

```wit
package etzhayyim:{app-domain};

world component {
    include kotodama:runtime/kotodama-component@1.0.0;
    import kotodama:contract/agreement@1.0.0;   // 必須
    import kotodama:contract/registry@1.0.0;     // 必須
    export etzhayyim:{domain}/{capability}@1.0.0;     // 必須
}
```

## Entity Pattern

同一契約の組織群は W Protocol Event Stream multi-tenant で管理:

```go
// Write: WRecord で AT Record として永続化
kotodama.WRecord("entity-registry", payload) // {"entity_id": "13-tokyo", "entity_name": "東京都", ...}

// Read: Kysely で typed row を取得
const db = createKyselyDb()
await db.selectFrom("vertex_entity_registry")
  .selectAll()
  .where("entity_id", "=", entityID)
  .execute()

// Read: graph projection も Kysely で取得
await db.selectFrom("vertex_gov_division")
  .select(["name"])
  .where("entity_id", "=", entityID)
  .execute()
```

## Build & Deploy

```bash
# Single app
cd 60-apps/etzhayyim-project-states/wasm/<app-dir>
etzhayyim build --no-check && etzhayyim deploy --no-smoke

# Multi-app (run per app directory)
etzhayyim deploy
```

## deps.etzhayyim.com Score

| Score | Weight | Source |
|---|---|---|
| contract_score | 5% | kotodama:contract/agreement import |
| capability_export_score | 5% | domain capability export |
| deps_link_score | 10% | parent/dependency import resolution |
| resource_flow_score | 5% | etzhayyim:gov-resource-flow WIT import/export coverage |
| div_score | 5% | kotodama:div WIT coverage (DIV-3 information/documents/materiel) |
