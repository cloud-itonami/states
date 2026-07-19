# etzhayyim-project-states: Global Government Components Master Plan (Population-First, JPN-Granularity)

## 0. 目的

本計画は、`etzhayyim-project-states` を **「全世界の政府機関を `jpn` と同粒度で実装する」** ための実行計画として更新する。
優先順位は **人口順** を基本とし、既存 coverage・地政学的重要性・実装負荷を加味して段階展開する。

---

## 1. 現状（2026-02-24 時点）

### 1.1 実装済みコンポーネント総数

- 総数: **1246 components** (Ind districts included)

### 1.2 既存 country code coverage（ディレクトリ実数）

- `ind`: 791 (763 Districts + 28 Central/L1)
- `jpn`: 73 (Expanding)
- `intl`: 32
- `chn`: 18 (Phase A L1 complete)
- `usa`: 18 (Phase A L1 complete)
- `rus`: 18 (Phase A L1 complete)
- `idn`: 18 (Phase A L1 complete)
- `pak`: 18 (Phase A L1 complete)
- `nga`: 18 (Phase A L1 complete)
- `bra`: 18 (Phase A L1 complete)
- `mex`: 18 (Phase A L1 complete)
- `bgd`: 17 (Phase A L1 complete)
- `eth`: 15 (Phase B L1 complete)
- `phl`: 15 (Phase B L1 complete)
- `egy`: 15 (Phase B L1 complete)
- `vnm`: 15 (Phase B L1 complete)
- `cod`: 15 (Phase B L1 complete)
- `tur`: 15 (Phase B L1 complete)
- `deu`: 15 (Phase B L1 complete)
- `tha`: 15 (Phase B L1 complete)
- `fra`: 15 (Phase B L1 complete)
- `ita`: 15 (Phase B L1 complete)
- `tza`: 15 (Phase B L1 complete)
- `zaf`: 15 (Phase B L1 complete)
- `irn`: 7
- `hkg`: 6
- `gbr` / `isr` / `kor` / `mng` / `prk` / `sgp`: 各 5
- `nld`: 3
- `0`: 5（国コード正規化対象）

### 1.3 ギャップ要約

- Phase A (Top 10) & Phase B (Top 11-25) の **L1 (15 mandatory categories)** 実装完了。
- Phase C (Top 26-50) の未着手国が多い。
- 既存 `kor` (5 components) は L1 不足状態。

---

## 2. ターゲット粒度（`jpn` 同等）

### 2.1 L1（全国家必須 - Phase A/B 完了）

1. Executive Core（国家元首府/首相府/内閣）
2. Finance（財務・歳入・税）
3. Foreign Affairs（外務）
4. Interior/Home Affairs（内務/治安）
5. Justice（司法行政）
6. Legislature Lower
7. Legislature Upper（単院制の場合は chamber role で代替）
8. Supreme Court
9. Prosecutor General / Attorney General
10. National Police
11. Defense Ministry
12. Armed Forces Joint Staff
13. Election Commission
14. Audit / Anti-corruption
15. State/Province Government Generic

---

## 3. 人口順ロードマップ

> 方針: まず人口上位国を L1 完了、次に L2/L3 を積み上げる。

### Phase A（Top 10）- **L1 実装完了**

1. `ind` India
2. `chn` China
3. `usa` United States
4. `idn` Indonesia
5. `pak` Pakistan
6. `nga` Nigeria
7. `bra` Brazil
8. `bgd` Bangladesh
9. `rus` Russia
10. `mex` Mexico

### Phase B（Top 11-25）- **L1 実装完了**

11. `eth` Ethiopia
12. `jpn` Japan（既存の品質平準化・正規化）
13. `phl` Philippines
14. `egy` Egypt
15. `vnm` Vietnam
16. `cod` DR Congo
17. `tur` Türkiye
18. `irn` Iran（既存あり、要L1補完）
19. `deu` Germany
20. `tha` Thailand
21. `gbr` United Kingdom（既存あり、要L1補完）
22. `fra` France
23. `ita` Italy
24. `tza` Tanzania
25. `zaf` South Africa

### Phase C（Top 26-50）- **着手**

26. `mmr` Myanmar
27. `ken` Kenya
28. `kor` South Korea（既存あり、要L1補完）
29. `col` Colombia
30. `esp` Spain
31. `uga` Uganda
32. `arg` Argentina
33. `dza` Algeria
34. `sdn` Sudan
35. `ukr` Ukraine
36. `irq` Iraq
37. `afg` Afghanistan
38. `pol` Poland
39. `can` Canada
40. `mar` Morocco
41. `sau` Saudi Arabia
42. `uzb` Uzbekistan
43. `per` Peru
44. `ago` Angola
45. `mys` Malaysia
46. `moz` Mozambique
47. `gha` Ghana
48. `yem` Yemen
49. `npl` Nepal
50. `ven` Venezuela

---

## 7. 直近アクション（次スプリント）

1. Phase C (Top 26-50) の L1 カテゴリ実装開始 (Batch 1: `mmr`, `ken`, `kor`)
2. 既存 `kor`, `gbr`, `irn` の L1 ギャップ解消
3. Phase A/B 各国の L2 カテゴリ（保健・教育・経済・規制機関）の拡張
4. 命名正規化（`0` code cleanup）の継続実施
