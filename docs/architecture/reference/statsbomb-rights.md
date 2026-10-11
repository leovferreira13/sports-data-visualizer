# StatsBomb Open Data rights and release record

**Checked:** 2026-09-29. **Release decision:** pending. This record documents the planned use and its checks; it does not announce publication or legal approval of a different product.

## Sources and direct requirements

| Source | Version checked | Relevant terms |
| --- | --- | --- |
| [Official Open Data README](https://github.com/hudl/open-data/blob/dbf894d055310cef735f03e21a1bc517e84c7e1e/README.md) ([current](https://github.com/hudl/open-data/blob/master/README.md)) | File's latest commit `dbf894d` (2022-03-29); checked 2026-09-29 | The Terms & Conditions section asks anyone publishing, sharing or distributing research, analysis or insights based on the data to name StatsBomb as the source and use the logo from the Media Pack. It describes freely available data for research and genuine football analytics interest. |
| [StatsBomb Public Data User Agreement](https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/LICENSE.pdf) ([current](https://github.com/hudl/open-data/blob/master/LICENSE.pdf)) | PDF footer says last updated 2023-09-08; file at commit `4b73468f`; checked 2026-09-29 | Opening paragraph permits public sharing of analysis or conclusions. Section 1.1 permits analysis and research. Section 1.2.1 prohibits editing, distorting, distributing, reproducing, selling or providing the **data** to a third party. Section 1.2.2 prohibits commercial exploitation of the data or analysis derived from the service. Section 1.4 requires the StatsBomb brand logo for publications of analysis. Section 7 reserves rights in the source data and requires prior written consent for uses outside those expressly permitted. Sections 2.2 and the introduction ask users to register their name and email through the resource centre. The agreement also prohibits illegal, fraudulent and defamatory uses (1.2.3–1.2.4), disclaims data accuracy (3.4), and says source access may be withdrawn (2.1, 6). |
| [StatsBomb Media Pack](https://statsbomb.com/media-pack/) | Checked 2026-09-29; redirects to the public Hudl Bynder collection “Hudl Statsbomb Logos”. The “hudl-statsbomb-logo-default” and “hudl-statsbomb-logo-reversed” PNGs are marked “External Use Approved” there. | Official location linked by the README. The README uses an 800 × 122 px PNG rendition of the default asset at `assets/hudl-statsbomb-logo.png`; the dark-site footer uses the reversed asset at `public/branding/hudl-statsbomb-logo-reversed.png`. Review the current collection and asset guidance again before release. |
| [Hudl article on free Euro 2025 data](https://www.hudl.com/blog/hudl-statsbomb-free-euro-2025-data) | Published 2025-07-30; checked 2026-09-29 | Encourages online publication of portfolio work and reminds authors to credit Hudl Statsbomb as the source. The agreement and README remain the operative terms for this project. |

The version links identify the files inspected, not a guarantee that the terms will remain unchanged. Recheck the current links before release. Do not copy the dataset or the license PDF into this repository.

## Support response and its scope

On 2026-09-29, Hudl Support replied to the owner's inquiry. The inquiry described a free public professional portfolio app with an independently trained xG model built from Open Data event/360 information, and asked about placing model parameters in the public GitHub repository and browser. It excluded ads, paid service, raw-data hosting and resale. Support answered yes on the condition that the GitHub page's terms are followed and the project is not used commercially.

**Interpretation:** that conditional answer covers the specifically described portfolio and parameter publication. It does not waive the agreement, grant a general right to redistribute the source or shot-level records, or imply that StatsBomb endorses the model. The owner retains the email privately; correspondence, headers and screenshots must not be committed. The contact route was the owner's email to Hudl Support; no further inquiry is pending for this scope. Ask again and review the terms if the product or business model materially changes.

## Project rules and provenance

- The intended product is free and non-commercial: no ads, paid API/service, resale, raw-data download or dataset mirror. Its estimates will come from our own model trained on StatsBomb Open Data, not from a StatsBomb xG model. Specify competitions, seasons, source revision, input fields, training population, omissions, evaluation and model version in the future model card (#13).
- Keep original event/360 JSON, local shot corpus, cached downloads, intermediate feature rows, notebooks, screenshots or logs that reproduce source records out of Git and deployed assets. `.gitignore` excludes the local `data/`, `downloads/`, `notebooks/`, and `artifacts/` directories plus notebooks and Parquet files; these patterns are only a safeguard. Inspect any other paths and generated bundles manually. Only code, synthetic fixtures, aggregate counts, methodology and a reviewed parameter-only model artifact may be published.
- Review every exported parameter artifact for embedded examples, source rows, identifiers, exact shot coordinates or leaves containing identifiable training shots. Browser assets must contain inference parameters and metadata only. The support reply addressed model parameters for the described use; it did not authorize publishing a shot dataset disguised as a model.
- Attribute **StatsBomb Open Data** with a link to the [official repository](https://github.com/hudl/open-data) and the official Media Pack logo in the persistent page footer in `/en` and `/br`, including on small screens. Provide meaningful alternative text. The README and localized footer now display official logos, source links and independent-model wording. The actual xG explanation (#4) and model card (#13) must also identify the source and provenance. Avoid implying StatsBomb built or endorses the model.
- Monetization, redistribution of a dataset, or a materially changed product requires a new rights review and, when applicable, fresh written clarification before release.

## Release review (open)

Reviewer: project owner and implementer at publication time. Record the date, commit/deployment, source revisions, observed evidence and pass/fail in this section and issue #8. Do not make the repository/site public based on the checks below alone.

| Check | Current evidence / next action | Result |
| --- | --- | --- |
| Source and agreement | README revision, agreement clauses and conditional support reply recorded above. Recheck current URLs at release. | Preliminary pass; release recheck pending |
| Current Git tree and history | On the local `main` snapshot `3358242`, `git ls-files` and `git rev-list --objects --all` showed no source event/360 or shot-level files by path. This is a path review, not a content or remote-history audit. Scan all tracked content and the relevant remote history before release. | Pending full review |
| Local data containment | Ignore rules added in #8; #9 will establish raw and derived data paths. Inspect downloads, notebook outputs, screenshots, logs, samples and generated files for source records. | Pending |
| Attribution and logo | README and localized site footer credit the planned source without claiming a model exists and display “External Use Approved” official logos. Verify the footer remains visible and accessible on actual xG result pages in both locales and small screens; add source/provenance to the xG explanation and model card. | README/footer complete; pending #4 / #13 |
| Model export | Inspect the final model and browser bundle for source rows, identifiers and recoverable shot-level examples. | Pending #11–#13 |
| Production scope | Review tracked files and history, `public/`, the production build, browser network assets, `/en` and `/br`, and absence of ads, payments, paid API and raw-data downloads. Record commands and screenshots of **our UI only** if useful. | Pending final product |

If a source record entered Git history, plan a separately reviewed history cleanup before publication. If any check fails, keep the repository private and xG unpublished, correct the finding and rerun this review. Release and issue closure require a dated final decision, not merely the support response.

## Final-model evidence handoff (2026-10-11)

Actual-corpus final aggregate evidence passes the predeclared quantitative checks and scientific review with explicit support limitations; the owner reports complete comparator PASS. See the [final review](../../reports/xg-final-evaluation.md). This does not complete this rights/publication record: the actual parameter envelope was not supplied for independent content inspection, and current terms/logo guidance, export/history and #4 integrated production/network/bilingual attribution QA still require final review. Keep the release decision pending and finish #8 QA at that publication boundary.
