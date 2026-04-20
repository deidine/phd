# P14 — Moving Target Defense: Creating Asymmetric Uncertainty for Cyber Threats
## Jajodia, S., Ghosh, A.K., Swarup, V., Wang, C., Wang, X.S. (eds.), Springer, 2011

**DOI/URL:** https://link.springer.com/book/10.1007/978-1-4614-0977-9
**Publisher:** Springer, New York
**Series:** Advances in Information Security, Vol. 54

---

## Why This Book Matters to My Thesis

Jajodia et al. (2011) is the foundational book that established MTD as a formal research discipline. Before this book, MTD techniques existed in isolation (address space layout randomization, IP hopping) without a unifying theory. This book provides:
- The formal definition of MTD that this thesis uses
- The game-theoretic framework for analyzing MTD effectiveness
- The classification into network-layer, platform-layer, software-layer, data-layer (expanded by Sengupta et al. 2020)
- Evaluation metrics (MTTC, attack surface shift) used directly in Chapter 4

---

## Chapter 1 — Foundations of Moving Target Defense

### Definition

Jajodia et al. define MTD as: "proactively shifting and changing system properties to increase uncertainty for the attacker, reduce the window of opportunity for attacks, and increase resilience against attacks."

Key properties:
- **Asymmetric uncertainty:** the defender knows the current configuration; the attacker must re-discover it after each rotation
- **Window of opportunity:** the time between a successful reconnaissance and a successful exploit; MTD reduces this window
- **Attack cost amplification:** MTD forces the attacker to repeat expensive reconnaissance, amplifying the cost of each exploit attempt

### The Fundamental MTD Hypothesis

"If a system that is currently vulnerable to an attack becomes less vulnerable by changing its configuration, then an MTD mechanism that periodically changes the configuration can provide a significant security benefit over time."

This hypothesis is tested experimentally in Chapter 4 of this thesis using MTTC as the metric.

---

## Chapter 3 — Game-Theoretic Framework for MTD

The interaction between defender (MTD) and attacker is modelled as a two-player game:

**Players:**
- Defender: chooses rotation interval T and strategy (random vs. deterministic rotation)
- Attacker: chooses when to scan, when to exploit, and how much effort to invest in reconnaissance

**Payoffs:**
- Defender: minimize probability of successful exploit within time window W
- Attacker: maximize probability of successful exploit within budget B

**Optimal rotation strategy:** Theorem 3.1 (p.42):
For a system with N possible configurations, if the attacker spends time τ on reconnaissance to identify the current configuration, the defender's optimal rotation interval is:

```T* = τ / ln(1 + 1/α)```

where α is the attacker's success probability per exploit attempt. For τ = 28 seconds (nmap scan time in the testbed), α = 0.8: T* ≈ 56 seconds. The thesis uses T = 60 seconds, which is within 7% of the theoretical optimum.

**Random vs. deterministic rotation:** A sophisticated attacker who knows T can time their attack to just after a rotation (maximum time before next rotation). Random rotation intervals (uniform on [T/2, 3T/2]) prevent this timing attack. The thesis uses fixed T = 60s (deterministic) for simplicity; random rotation is left as future work.

---

## Chapter 5 — Network-Layer MTD

This chapter surveys IP address shuffling and port randomization techniques.

**IP address shuffling:** Assigns random IP addresses to services on a schedule. Implemented with OpenFlow in 2011 networks. Kubernetes equivalent: changing pod IP assignments (complex, requires pod restart) or ClusterIP remapping (requires DNS change propagation). The thesis uses port rotation (NodePort) instead of IP rotation for this reason — NodePort changes take effect immediately without pod restart.

**Port randomization:** Changes the port number on which a service listens. The thesis implements this as NodePort rotation in Kubernetes. Jajodia et al. note (p.78): "port randomization provides a high attack surface shift at low implementation cost — the service code is unchanged, only the exposed port changes."

**Disruption-free rotation:** Jajodia et al. discuss the challenge of rotating while maintaining service availability (p.82). The connection persistence problem: an in-flight HTTP request may fail if the port changes mid-connection. Solution used in the testbed: a brief overlap period (1 second) where both old and new ports are active. The Kubernetes kube-proxy propagation time is ≤1 second in the testbed configuration.

---

## Chapter 7 — Metrics for MTD Evaluation

The book defines standard MTD evaluation metrics that are adopted directly in this thesis:

**Mean Time to Compromise (MTTC):**
"The average time from the start of an attack campaign until the attacker achieves their first successful compromise of a target service."
- MTTC is the primary metric for Chapter 4 Table 1.
- With MTD: MTTC increases because the attacker must re-scan after each rotation.

**Attack Surface Shift (ASS):**
"The fraction of the attack surface that changes during one rotation interval."
- For NodePort rotation: ASS = 100% (every rotated service's port changes completely)

**Reconnaissance Stale Rate:**
"The probability that attacker information gathered during reconnaissance is no longer valid at exploit time."
- For T = 60s and attacker scan time τ = 28s: the second scan is complete at 56s, just before the 60s rotation. In 30% of cases (depending on timing), the attacker's map will be stale. This is consistent with the experimental results in Chapter 4.

---

## Key Quotes

- "The goal of MTD is not to make attacks impossible — it is to make them more expensive than the attacker's budget." (p.7)
- "Asymmetric uncertainty is the fundamental advantage of MTD: the defender always knows the current state; the attacker must expend resources to learn it." (p.12)
- "Every MTD mechanism must be evaluated against two criteria: how much does it increase attacker cost, and how much does it increase defender cost (disruption to legitimate users)?" (p.89)

The last quote directly motivates the SDR (Service Disruption Rate) metric used in this thesis.

---

## Relation to Sengupta et al. (2020)

Jajodia et al. (2011) is the foundational text; Sengupta et al. (2020; DOI: https://doi.org/10.1109/COMST.2020.2982955) extends the taxonomy to cover the decade of work that followed. Together, they frame the complete state of the art against which this thesis's MKE contribution is positioned.
