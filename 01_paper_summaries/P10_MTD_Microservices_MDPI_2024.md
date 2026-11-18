# P10 — Zhou, Y., Cheng, G. & Du, K. (2025). Enhancing Microservice Security Through Adaptive Moving Target Defense Policies to Mitigate DDoS Attacks in Cloud-Native Environments
**Venue:** Future Internet, MDPI, 17(12), 580 — published 2025-12-16
**Date read:** Month 3, Week 1
**DOI:** https://doi.org/10.3390/fi17120580
**Free PDF:** https://www.mdpi.com/1999-5903/17/12/580

---

## Why I read this
This is the closest existing paper to my Contribution 1 (MTD for microservices).
I must know it thoroughly to explain my differentiation.

**Correction (verified against Crossref metadata, 2026):** the notes below
originally described a different paper than the one at this DOI — wrong
year (2024, not 2025), wrong platform (claimed Docker Swarm; the real
abstract never mentions it), wrong method (claimed simple threshold-based
detection; the real paper uses Deep Reinforcement Learning), and invented
numbers (73% DDoS reduction, <2% disruption) that don't appear in the
abstract. This file now reflects only what the verified abstract actually
says. I was not able to fetch the full PDF (MDPI returned 403 to automated
access), so anything beyond the abstract — detailed methodology, the exact
testbed, full results tables — still needs to be checked against the real
PDF before being cited anywhere else.

---

## What the Paper Does (from the verified abstract)

Proposes **ScaleShield**, an adaptive Moving Target Defense framework for
cloud-native microservices that:
- Targets resource-exhaustion DDoS attacks that propagate along service
  call chains and closely mimic legitimate traffic (evading traditional
  detection)
- Formulates defense as a Markov Decision Process over multi-dimensional,
  discrete defense actions
- Uses a **Multi-Dimensional Double Deep Q-Network (MD3QN)** — i.e. Deep
  Reinforcement Learning — to learn coordinated, attack-aware, cost-aware
  defense policies, rather than a fixed or threshold-triggered rotation
  schedule

**Results (as stated in the abstract):** near-100% defense success rate;
compromised nodes reduced to zero within ~5 steps; up to 72% reduction in
service latency under dynamic attacks; >94% resource efficiency maintained.
The abstract reports no precision/recall/F1/FPR figures and does not name
Docker Swarm as the test platform — so no direct detection-accuracy
comparison against this paper is actually possible from what's verified.

---

## Actual Differentiation From This Paper

This paper and this thesis target different problems, so the comparison is
about scope, not a head-to-head metric gap:

**1. Different threat model / goal.** ScaleShield is purpose-built for
resource-exhaustion DDoS mitigation via adaptive endpoint/action rotation.
This thesis's three-layer framework additionally targets authorization
policy correctness (FV-Zanzibar) and statistical lateral-movement/DDoS
detection on authorization logs specifically (SAAD) — a different data
source than ScaleShield's traffic-based DRL policy.

**2. Learning-based vs. statistical/formal.** ScaleShield *does* use
machine learning (DRL) for policy selection — this is not a "no-ML vs. ML"
gap the way earlier notes framed it. The actual differentiation is that
this thesis's detection and verification components are interpretable and
training-free by design (Shannon entropy + CUSUM, TLA+ model checking),
which is a deliberate trade-off against ScaleShield's learned-policy
approach, not a strict improvement on it.

**3. Authorization integration.** The verified abstract does not describe
any authorization-system integration (Zanzibar/Keto or otherwise). If
confirmed by the full text, this would remain a genuine point of
differentiation: this thesis rotates NodePort values *and* authorization
tuples together, and formally verifies the authorization policy itself.

**4. Formal verification.** The abstract does not mention formal methods.
If confirmed by the full text, FV-Zanzibar's TLA+ verification remains
differentiating — DRL-based policy learning provides no safety proof, by
construction.

---

## Table: My System vs. This Paper

| Feature | ScaleShield (MDPI 2025) | My Thesis |
|---------|--------------------------|-----------|
| MTD endpoint/action rotation | ✓ | ✓ |
| Machine learning used | **Yes (DRL / MD3QN)** | No (statistical + formal only) |
| Authorization integration (Keto) | Not described in abstract | ✓ |
| Formal verification (TLA+) | Not described in abstract | ✓ |
| Statistical detection (CUSUM + entropy) | Not described in abstract | ✓ |
| Primary target | Resource-exhaustion DDoS | MTD + authorization correctness + statistical detection |

Rows marked "Not described in abstract" are **not confirmed absent** —
they simply weren't verifiable without the full PDF, and should not be
cited elsewhere as a settled comparison until checked.

This comparison previously appeared, in its uncorrected form, in Chapter 2
§2.7 and in the conference paper's Table 5 / §4.5 — both have been
corrected to match this file.
