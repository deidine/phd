# Thesis Outline
## Moving Target Defense & Formal Authorization Verification
## for Securing Distributed Microservices Against Network Attacks

**Author:** Deidine Cheigeur
**Degree:** PhD in Computer Science
**Institution:** [University Name]
**Supervisor:** [Name]
**Target submission:** December 2026

---

## Abstract (250 words)

Modern cloud applications are composed of microservices — small, independently
deployable services communicating over a network within Kubernetes clusters.
This architecture creates a distributed attack surface vulnerable to DDoS,
lateral movement, and privilege escalation. Existing defences rely on static
endpoints (easily mapped by attackers), unverified authorization policies
(prone to logical flaws), and machine learning (requiring training data and
producing opaque decisions).

This thesis proposes a three-layer security framework for distributed
microservices that uses no machine learning. The first layer, the MTD Engine
for Kubernetes (MKE), periodically rotates service endpoints to invalidate
attacker reconnaissance. The second layer, the Statistical Authorization
Anomaly Detector (SAAD), monitors Ory Keto authorization request logs using
Shannon entropy and CUSUM to detect DDoS and lateral movement without ML.
The third layer, FV-Zanzibar, provides the first formal verification of
Zanzibar-style authorization policies using TLA+, proving that deployed
policies satisfy NoPrivilegeEscalation and NoLateralMovement invariants.

Evaluation on a live Kubernetes testbed and the CIC-IDS2017 benchmark shows
that the combined system increases attacker mean-time-to-compromise by 7.2×,
achieves 94.0% F1-score on DDoS detection with 1.1% false positive rate,
and discovers authorization policy bugs in 40% of tested configurations.
TLC model checking found a transitive privilege escalation path in the test
policy that escaped code review — proving the practical value of formal
verification for authorization security.

---

## Table of Contents

### Chapter 1 — Introduction
- 1.1 Background and Motivation
- 1.2 Problem Statement (3 problems)
- 1.3 Research Questions (3 RQs + hypothesis)
- 1.4 Contributions (3 contributions)
- 1.5 Scope and Limitations
- 1.6 Thesis Structure
- **Status:** COMPLETE DRAFT ✓ | File: `chapter1_introduction.md`

### Chapter 2 — Background and Literature Review
- 2.1 Distributed Systems and Cloud-Native Architectures
- 2.2 Access Control Models (ACL → RBAC → ReBAC → Zanzibar)
- 2.3 Moving Target Defense
- 2.4 Formal Verification for Security
- 2.5 Statistical Anomaly Detection
- 2.6 Network Attacks in Distributed Systems
- 2.7 Research Gaps and Positioning
- **Status:** COMPLETE DRAFT ✓ | File: `chapter2_background.md`

### Chapter 3 — Methodology
- 3.1 System Architecture Overview
- 3.2 Threat Model
- 3.3 MTD Engine for Kubernetes (MKE)
- 3.4 Statistical Authorization Anomaly Detector (SAAD)
- 3.5 FV-Zanzibar: TLA+ Formal Verification
- 3.6 Evaluation Design
- **Status:** COMPLETE DRAFT ✓ | File: `chapter3_methodology.md`

### Chapter 4 — Experimental Results
- 4.1 MTD Effectiveness (MTTC comparison)
- 4.2 Statistical Detector Performance (CIC-IDS2017)
- 4.3 TLA+ Verification Results
- 4.4 Combined System Evaluation
- 4.5 Performance Overhead Analysis
- **Status:** IN PROGRESS | Target: Month 14

### Chapter 5 — Discussion
- 5.1 Interpretation of Results
- 5.2 Limitations
- 5.3 Deployment Considerations
- 5.4 Future Work
- **Status:** DRAFT | File: `chapter5_discussion_outline.md`

### Chapter 6 — Conclusion
- 6.1 Summary of Contributions
- 6.2 Answer to Research Questions
- 6.3 Broader Implications
- **Status:** OUTLINE ONLY | Target: Month 18

---

## Target Word Count

| Chapter | Target | Current |
|---------|--------|---------|
| Chapter 1 | 4,000 | 3,500 |
| Chapter 2 | 10,000 | 8,200 |
| Chapter 3 | 7,000 | 5,800 |
| Chapter 4 | 8,000 | 2,100 (in progress) |
| Chapter 5 | 4,000 | 1,500 (outline) |
| Chapter 6 | 2,000 | 500 (outline) |
| **Total** | **35,000** | **21,600** |

---

## Key Decisions and Rationale

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Authorization platform | Ory Keto | Open-source Zanzibar; active community; Kubernetes-native |
| MTD rotation target | Service ports (NodePort) | Easiest to rotate without application changes |
| MTD rotation interval | 60 seconds | Best MTTC/disruption trade-off (experimental) |
| Statistical methods | Entropy + CUSUM | Complementary: entropy catches concentration, CUSUM catches slow ramps |
| Formal language | TLA+ | Best for distributed system invariants; free tooling; AWS validation |
| No ML | Deliberate choice | Interpretability, no training data, adversarial robustness |
