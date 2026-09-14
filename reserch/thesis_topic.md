# Thesis Topic Assignment
## Supervisor: Claude (Acting)  |  Candidate: Deidine Cheigeur  |  June 2026

---

## Assigned Thesis Title

> **"Moving Target Defense and Formal Authorization Verification
> for Securing Distributed Microservices Against Network Attacks"**

---

## Field

**Discipline:** Computer Science — Distributed Systems & Cybersecurity
**Approach:** Algorithmic security — NO machine learning
**Pillars:** Moving Target Defense · Statistical detection · Formal methods · Authorization

---

## The Problem

Cloud applications are built from many small services (microservices) running
inside Kubernetes clusters. Once an attacker gets inside one service, three
things happen:

| Attack | What happens |
|--------|-------------|
| **Reconnaissance** | Attacker maps which services exist, their IPs, their ports |
| **Lateral movement** | Attacker jumps from one compromised service to others |
| **Privilege escalation** | Attacker gains permissions they were never supposed to have |

Current defences fail because:
1. Service IPs and endpoints are **static** — easy to map and exploit
2. Authorization rules are **never formally checked** for logical flaws
3. Anomaly detection relies on ML — complex, black-box, hard to deploy

---

## Research Question

> **"Can Moving Target Defense combined with statistically-monitored,
> formally-verified relationship-based authorization prevent attackers
> from mapping, moving through, and escalating privileges in
> distributed cloud microservices — without any machine learning?"**

---

## Your Three Contributions (No ML)

### Contribution 1 — MTD Engine for Kubernetes
Dynamically and periodically **rotate** service endpoints, internal IPs,
ports, and API paths inside Kubernetes. An attacker who maps the system
at time T finds a completely different topology at time T+1.

- Implemented as a Kubernetes controller (Go or Python)
- Rotation period configurable (e.g., every 60 seconds)
- Services still reachable by legitimate clients via service discovery
- Evaluated: does it stop lateral movement? How much does it slow attackers?

**Why novel:** MTD for Kubernetes at the service-mesh level is unaddressed.
The 2024 MDPI paper on MTD for microservices does not handle authorization.

### Contribution 2 — Statistical Anomaly Detection (No ML)
Detect DDoS and abnormal access patterns using **entropy** and **CUSUM**
(Cumulative Sum control chart) — pure statistics, zero ML.

- **Shannon entropy** of request rate per service pair: drops sharply during DDoS
- **CUSUM** applied to per-service request counts: detects slow-and-low attacks
- **Rate thresholds** per Zanzibar authorization check: detects brute-force permission probing
- All thresholds computed from normal-traffic baselines — no training, no model

**Why novel:** All recent cloud IDS papers use ML. Pure-statistical detection
for microservices with authorization-layer monitoring is a genuine gap.

### Contribution 3 — Formal Verification of Authorization Policies
Use **TLA+** to formally model and verify the Zanzibar/Keto authorization
graph and prove two security invariants:

1. **No privilege escalation:** A subject can never reach a resource
   above their permission level, even after a chain of service calls
2. **No unauthorized lateral movement:** A compromised service
   cannot use its own permissions to authorize access to unrelated services

Policies written in Keto's OPL (Ory Permission Language) are translated
to TLA+ specs and model-checked with TLC.

**Why novel:** Zanzibar/Keto has no formal security verification in the
literature. No paper has combined MTD with formally-verified authorization.

---

## Connection to Ory Keto / Zanzibar

Ory Keto (https://github.com/ory/keto) is your implementation platform.
It implements Google's Zanzibar paper (USENIX ATC 2019) in open source.

You use Keto as:
- The authorization decision point in your distributed microservices testbed
- The source of authorization logs for Contribution 2 (statistical detection)
- The system whose policies you formally verify in Contribution 3

This makes your thesis **practical and deployable** — not theoretical.

---

## Technology Stack (No ML)

| Component | Tool |
|-----------|------|
| Distributed system testbed | Kubernetes (minikube) |
| Authorization | Ory Keto + OPL policies |
| MTD controller | Python or Go (Kubernetes client library) |
| Statistical detection | Python: numpy, scipy (entropy, CUSUM) |
| Formal verification | TLA+ + TLC model checker (free) |
| Network attacks | kube-bench, wrk, hping3 (attack tools) |
| CI | GitHub Actions |

---

## Datasets / Evaluation

| Source | What you measure |
|--------|-----------------|
| CIC-IDS2017 | Baseline network attack traffic (DDoS, port scan) |
| Your Kubernetes testbed | Live attack vs. MTD rotation — time to exploit |
| Keto authorization logs | False positive rate of statistical detector |
| TLA+ model checker output | Formally proved invariants |

---

## The Gap (Why This is Novel)

| Gap | Evidence |
|-----|----------|
| No MTD system integrated with Zanzibar authorization | Not in any paper |
| No formal verification of Keto/Zanzibar policies | Zanzibar paper (2019) has no formal proof |
| No statistical (non-ML) IDS for microservices with authorization layer | All current papers use ML |

---

## Expected Publications

| Paper | Target Venue |
|-------|-------------|
| "MTD for Kubernetes Microservices: A Service-Mesh Approach" | IEEE CLOUD / ACM CODASPY |
| "Formal Verification of Zanzibar Authorization Policies in Distributed Systems" | ACM CCS Workshop / ESORICS |
| Full journal paper | IEEE Transactions on Dependable and Secure Computing |
