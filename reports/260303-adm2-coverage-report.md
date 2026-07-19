# ADM2 Coverage Report

- Date: 2026-03-03 (JST)
- Scope: `60-apps/etzhayyim-project-states/wasm`
- Population source: geoBoundaries API (`gbOpen/ALL/ADM2`)

## Current Coverage

- Implemented ADM2 components (directory pattern contains `-dst-`): `762`
- Global ADM2 denominator (sum of `admUnitCount`): `49,363`
- Coverage: `762 / 49,363 = 1.5437%`

## Delta From Previous Baseline

- Previous implemented ADM2 count: `752`
- Current implemented ADM2 count: `762`
- Net increase: `+10`
- Coverage increase: `+0.0203` percentage points (`1.5234% -> 1.5437%`)

## Notes

- This report uses `-dst-` as ADM2 proxy for component directories.
- A stricter name filter (`org-gov-{iso3}-...-dst-`) currently yields `752`; this indicates legacy/non-uniform naming still exists in part of the dataset.
