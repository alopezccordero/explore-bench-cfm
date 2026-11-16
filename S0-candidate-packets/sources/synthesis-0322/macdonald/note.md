# Full-text evidence — MacDonald & Smith active sensing

Retrieved 2026-11-16 ~03:24 CST. Title: **Active sensing for motion planning in uncertain environments via mutual information policies**. Authors: Ryan A. MacDonald; Stephen L. Smith. IJRR 38(2–3), 146–161, **2019 issue; online 2018-05-09**. DOI **10.1177/0278364918772024**. Crossref direct metadata distinguishes online/print dates; OpenAlex uses 2018; S2 uses 2019. This is a date-convention discrepancy, not different papers.

## Actual access and inspected full text
Author publication list `https://ece.uwaterloo.ca/~sl2smith/publications.html` links the authorized manuscript `https://ece.uwaterloo.ca/~sl2smith/papers/2017IJRR-Active.pdf`. Saved as `sources/synthesis-0322/macdonald.pdf`; page-marked extraction `macdonald.txt`. Manuscript has editorial placeholder header and 23 pages; do not call it publisher pagination/version-of-record. Inspected abstract/introduction, model §§3.1–3.2, §5.1 pp11–14, §5.3 p15, §6 pp15–17, §7.2–7.3 pp19–21, conclusion. SAGE PDF returned 403 challenge, not full text; official arXiv exact-title query returned zero. Author route then succeeded. No permission to redistribute code/data or execute established by this PDF.

## Supported claims, at their actual scope
- Model supplies a prior distribution over candidate graph edge sets; local sensing has known action and travel costs. Physical travel-to-sensing is already central, unlike purely computational edge checking.
- §5.1 eqs(4)–(6) select information about **entire environment identity X**, NOT a binary start–goal connectivity event. Eqs(9)–(11) combine cost-to-go/pruning with entropy (weighted product or tuned additive form). Therefore 'task-aware information rather than uncertain area' is not a fresh unoccupied idea; their explicit score is nonetheless not identical to our binary query proxy.
- §5.3 gives an exponential dynamic-programming comparator with matched stipulated prior. Distinguish this from an omniscient current-world route oracle: knowing the prior is not knowing which world occurred.
- §7.2 already varies the fraction of worlds with a path to goal and compares heuristic versus optimum; reports structure-related sensitivity of entropy/cost weights. These reported numerical findings belong to this source, not to our study; no numbers are imported as predicted effects.
- §7.3 perturbs realized edges to make priors inaccurate; contradiction triggers A* fallback. Thus 'information can become harmful when the prior is wrong' is already occupied broadly.
- §6 explicitly discusses noisy observations and structured correlated fault types. Do not present a general correct-noise-likelihood benefit as novel on its strength.

## A-specific inference / repair, NOT a measured finding
If every supported world has a known guaranteed fallback start–goal route, the binary connectivity event C is identically true. Then its entropy and information gain are zero, even though observing a shortcut may change the cost-optimal route. This follows from the event definition; it is an analytic test case to build later, NOT an executed pilot. A cannot sell a two-route toy as an open question. Its residual value is a scoped **proxy sufficiency/replication audit**, spanning varying reachability versus route-cost ambiguity, with world-identity information and same-prior one-step decision value as comparators. A null should mean the cheaper proxy is adequate within declared tolerance and regime, not just 'not significant.'

## Metadata resolution actually performed
Crossref title search and direct DOI, OpenAlex DOI direct, and S2 batch all returned matching title/authors/DOI. S2 ID `8d25fd25b353e29f6752d4c4ddb4fd0f22016934`. Raw responses in this directory. OpenAlex anonymous search returned 503 but direct DOI succeeded; this is service failure, not absent literature. Not a completed S1 citation graph crawl.

## Limits
No direct CFM posterior experiment, binary connectivity-vs-cell-variance controlled study, or evaluator implementation for our exact RQ verified here. General idea and many regimes are prior art, so specificity is necessary and novelty remains unestablished.
