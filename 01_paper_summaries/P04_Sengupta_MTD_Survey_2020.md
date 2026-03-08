# P04 — Sengupta et al. (2020). A Survey of Moving Target Defenses for Network Security
**Venue:** IEEE Communications Surveys & Tutorials, 22(3), 1909–1941
**Date read:** Month 2, Week 1
**DOI:** https://doi.org/10.1109/COMST.2020.2982955

---

## Why I read this
This is the foundational MTD survey. It maps the entire field and confirms that
applying MTD to cloud-native Kubernetes microservices is an open problem.

---

## Core Idea of MTD

Traditional security is **static**: firewall rules, access control lists, and service
endpoints do not change. This gives attackers a fundamental advantage: they can invest
unlimited time in reconnaissance and the information they gather stays valid.

MTD inverts this asymmetry: **make the system dynamic** so that reconnaissance becomes
outdated and exploits that worked yesterday fail today.

**Key asymmetry equation:**
- Attacker cost of reconnaissance: O(n) — scan once, map everything
- With MTD, attacker must re-scan continuously — cost becomes O(n × 1/rotation_period)
- At high enough rotation frequency, the cost of maintaining an accurate map exceeds the attacker's resources

---

## Four Categories of MTD Techniques

| Category | What changes | Examples | Effectiveness |
|----------|-------------|---------|--------------|
| **Network-layer** | IP addresses, ports, routing paths | IP hopping, port hopping | High against scanning, medium against persistent attackers |
| **Platform-layer** | OS type, runtime libraries, compiler flags | Diversification, N-variant systems | High against memory exploits |
| **Software-layer** | Code layout, API endpoints, function names | Address Space Layout Randomisation (ASLR), API versioning | Medium-high |
| **Data-layer** | Data encoding, storage location, format | Instruction Set Randomisation, data diversity | Medium |

My thesis focuses on **network-layer + software-layer MTD** in Kubernetes:
rotating ClusterIPs (network) and service API paths (software).

---

## Key Findings Relevant to My Thesis

**Finding 1:** MTD reduces attacker success rate by 60–80% in simulation studies. However, most studies are in traditional flat networks. The survey explicitly states:
> *"Application of MTD to cloud-native container-orchestrated environments remains an open research direction."*
This sentence is quoted in my Chapter 2, Section 2.7 (Research Gaps).

**Finding 2:** MTD has a cost — legitimate clients must always be able to find services. In traditional networks this is solved with static DNS. In Kubernetes I solve it using Keto relationship tuples as the dynamic service registry — a novel combination.

**Finding 3:** MTD alone is insufficient. The survey recommends combining MTD with a detection layer. My Contribution 2 (statistical detector) serves this role.

---

## MTD Evaluation Metrics (from this paper)

The survey defines metrics I adopt in Chapter 4:
- **Mean Time to Compromise (MTTC):** How long does an attacker need to successfully exploit the system? MTD should increase MTTC.
- **Attack Surface Shift:** Percentage of attack surface that changes per rotation cycle.
- **Service Disruption Rate:** Percentage of legitimate requests that fail due to MTD activity.

Target from literature: MTTC increase > 5×, service disruption < 1%.

---

## Limitations of Existing MTD Work

1. Most papers evaluate MTD in simulated, static networks — not live Kubernetes clusters
2. No paper integrates MTD with a formally-verified authorization layer
3. No paper evaluates MTD specifically against lateral movement attacks
4. Cost models are oversimplified (assume uniform attacker capability)

**All four limitations are addressed in my thesis.**
