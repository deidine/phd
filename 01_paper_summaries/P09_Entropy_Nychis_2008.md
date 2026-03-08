# P09 — Nychis et al. (2008). An Empirical Evaluation of Entropy-based Traffic Anomaly Detection
**Venue:** ACM Internet Measurement Conference (IMC 2008)
**Date read:** Month 2, Week 3
**DOI:** https://doi.org/10.1145/1452520.1452539
**Free PDF:** https://www.cs.cmu.edu/~gng/papers/nychis08entropies.pdf

---

## Why I read this
Shannon entropy is the first half of my statistical detector (Contribution 2).
This paper empirically validates that entropy detects DDoS reliably on real traffic.

---

## The Entropy Hypothesis

During **normal traffic**, requests are distributed across many services and destinations.
Entropy H is **high** — many equally probable destinations.

During a **DDoS attack**, all traffic floods one target.
Distribution concentrates on one destination.
Entropy H **drops sharply**.

Mathematically:
```
H(t) = -Σᵢ pᵢ(t) × log₂(pᵢ(t))

pᵢ(t) = fraction of traffic going to destination i during window t

Maximum H = log₂(N)  when traffic is uniformly distributed (N destinations)
Minimum H = 0        when all traffic goes to one destination
```

---

## What the Paper Proves

Using 6 months of real backbone traffic from a Tier-1 ISP, the authors:
1. Computed per-flow entropy at 1-minute intervals
2. Cross-referenced with known attack events from NOC logs
3. Measured detection performance

**Results:**
- DDoS attacks cause entropy drops detectable with **> 95% recall** at < 2% false alarm rate
- Port scan attacks cause entropy spikes (many different destination ports)
- Normal traffic fluctuations do not cause threshold crossings

**Key finding for my thesis:** Entropy is effective even when the attacker tries to spread traffic (distributed DDoS from many sources), because the *destination* distribution still concentrates on the victim service.

---

## My Adaptation for Microservices

Original paper: monitors entropy of IP destination distribution.
My adaptation: monitors entropy of **Keto authorization check distribution** per service.

```python
# During normal operation:
# svc_a checks: db (40%), cache (30%), auth (20%), logger (10%)
# Entropy: H = -(0.4 log 0.4 + 0.3 log 0.3 + 0.2 log 0.2 + 0.1 log 0.1) = 1.85 bits

# During DDoS targeting svc_a:
# All authorization checks from outside: svc_a (98%), other (2%)
# Entropy: H = -(0.98 log 0.98 + 0.02 log 0.02) = 0.14 bits
# Alert: H dropped by 92% → attack detected
```

This adaptation is novel — no previous paper applies entropy to service-level authorization logs.

**Alert threshold:** H(t) < (1 - 0.40) × H_baseline = 0.60 × H_baseline
(40% drop triggers alert — tuned on my testbed to give < 1% false alarm rate)
