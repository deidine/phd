# P10 — (2024). Enhancing Microservice Security Through Adaptive MTD Policies to Mitigate DDoS Attacks in Cloud-Native Environments
**Venue:** Future Internet, MDPI, 17(12), 580 — 2024
**Date read:** Month 3, Week 1
**DOI:** https://doi.org/10.3390/fi17120580
**Free PDF:** https://www.mdpi.com/1999-5903/17/12/580

---

## Why I read this
This is the closest existing paper to my Contribution 1 (MTD for microservices).
I must know it thoroughly to explain my differentiation.

---

## What the Paper Does

Proposes an adaptive MTD system for Kubernetes microservices that:
- Monitors DDoS traffic in real time
- When attack is detected, **increases rotation frequency** of service endpoints
- Adapts rotation speed based on attack intensity
- Evaluated on a 3-service Kubernetes testbed

**Results:** 73% reduction in successful DDoS connections during attack, < 2% service disruption for legitimate clients.

---

## Three Critical Gaps in This Paper

This is very important for my thesis positioning:

**Gap 1 — No authorization integration:**
This paper rotates service IPs/ports but does not integrate with an authorization system.
A sophisticated attacker who compromises one service can still use that service's
authorization credentials to access other services — the rotation does not stop lateral movement.
**My system integrates MTD with Keto — rotating the authorization relationships alongside endpoints.**

**Gap 2 — No formal security guarantees:**
The paper evaluates MTD effectiveness empirically but provides no formal proof
that the system prevents any class of attack. It cannot claim "privilege escalation is impossible."
**My system formally verifies (via TLA+) that the authorization policy prevents escalation.**

**Gap 3 — Detection layer missing:**
The paper detects DDoS using a simple threshold — if traffic exceeds X packets/second, trigger MTD.
This misses slow-ramp attacks and authorization-layer attacks.
**My system uses CUSUM + entropy which are sensitive to gradual changes and auth anomalies.**

---

## Table: My System vs. This Paper

| Feature | MDPI 2024 | My Thesis |
|---------|-----------|-----------|
| MTD endpoint rotation | ✓ | ✓ |
| Authorization integration (Keto) | ✗ | ✓ |
| Formal verification (TLA+) | ✗ | ✓ |
| Statistical detection (CUSUM + entropy) | ✗ | ✓ |
| Lateral movement defence | ✗ | ✓ |
| Machine learning | ✗ | ✗ |

This comparison table appears in my Chapter 2, Section 2.7 and in the conference paper.
