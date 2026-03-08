# P08 — Blazek et al. (2001). A Novel Approach to Detection of DoS Attacks via Adaptive Sequential and Batch-Sequential Change Point Detection Methods
**Venue:** IEEE Workshop on Information Assurance and Security
**Date read:** Month 2, Week 3
**DOI:** https://doi.org/10.1109/IWIAS.2001.935077
**Request PDF:** https://www.researchgate.net/publication/3892699

---

## Why I read this
CUSUM (Cumulative Sum) is one of the two statistical methods in my Contribution 2.
This paper proves CUSUM works for DoS detection — I extend it to microservices.

---

## What is CUSUM?

CUSUM (Page, 1954) is a sequential change-point detection algorithm originally
designed for quality control in manufacturing. It detects when a process
shifts from its normal distribution.

**Formula:**
```
S(0) = 0
S(t) = max(0, S(t-1) + (x(t) - μ₀ - k))

x(t)  = observed value at time t (e.g., request rate to a service)
μ₀    = baseline mean (computed from normal traffic)
k     = allowance = 0.5 × expected shift magnitude
S(t)  = cumulative sum (resets to 0 if it goes negative)

ALERT when S(t) > h
h     = detection threshold (tuned to control false alarm rate)
```

**Intuition:** CUSUM accumulates small persistent increases. A single spike (normal burst) briefly raises S then resets. A sustained increase (DDoS onset) keeps S growing until it crosses h.

---

## What the Paper Proves

Using network traffic simulation with embedded DoS attacks, the authors show:
- CUSUM detects volumetric DoS with **mean detection delay of 3.2 seconds**
- False alarm rate: **< 0.5%** at threshold h = 5σ
- Outperforms threshold-only detection (which misses slow-ramp attacks)
- Does not require any labelled attack data for training

**Why this matters for my thesis:** No training data = no ML needed.
CUSUM computes its own baseline from the first N minutes of normal traffic.

---

## How I Extend This to Microservices Authorization

Original paper monitors: total network packet rate (one signal).
My extension monitors: **per-service-pair Keto authorization request rate** (many signals simultaneously).

For each pair (service_A → service_B), I run an independent CUSUM instance.
If service_A suddenly starts requesting authorization checks to access service_C
(a service it never normally communicates with), the CUSUM for that pair
will trigger an alert — detecting lateral movement at the authorization layer.

**This is novel.** No previous paper applies CUSUM to authorization request logs.

---

## Parameters I Use (from calibration experiments)

| Parameter | Value | Justification |
|-----------|-------|--------------|
| Baseline window | 600 seconds | 10 minutes of normal startup traffic |
| k (allowance) | 0.5 × σ_baseline | Standard CUSUM recommendation |
| h (threshold) | 5σ_baseline | Corresponds to < 1% false alarm rate in my testbed |
| Update interval | 1 second | Real-time detection requirement |
