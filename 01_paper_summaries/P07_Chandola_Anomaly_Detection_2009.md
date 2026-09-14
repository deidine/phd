# P07 — Chandola et al. (2009). Anomaly Detection: A Survey
**Venue:** ACM Computing Surveys, 41(3), Article 15
**Date read:** Month 2, Week 2
**Citations:** ~8,000 (one of the most cited CS papers)

---

## Why I read this
My Contribution 2 uses statistical anomaly detection (no ML).
This survey maps all anomaly detection methods — I need to know
which statistical approaches are appropriate and why.

---

## Definition

An anomaly is an observation that deviates significantly from expected behaviour.
The challenge: "significantly" must be defined rigorously, and the definition of
"expected" must be established from normal data.

---

## Three Paradigms of Anomaly Detection

| Paradigm | How it works | Requires labels? | My choice? |
|----------|-------------|-----------------|------------|
| **Supervised** | Train classifier on labelled normal+attack data | Yes | No — labels unavailable in real deployments |
| **Semi-supervised** | Train on normal data only; flag deviations | Normal only | Possible but requires stable baseline |
| **Unsupervised / Statistical** | Define expected distribution; compute test statistic; alert if threshold exceeded | No | YES — this is Contribution 2 |

---

## Statistical Methods Surveyed (Most Relevant to Me)

**1. Parametric statistical tests:**
Model the data as following a known distribution (e.g., Gaussian). Use hypothesis testing (z-test, χ² test) to flag observations as anomalous.
- Limitation: Network traffic is rarely Gaussian. Heavy-tailed distributions are common.

**2. Non-parametric tests:**
Do not assume a distribution. Use order statistics, kernel density estimation, or rank tests.
- Better fit for network traffic.

**3. Information-theoretic measures (Shannon entropy):**
- High entropy = many equally probable outcomes = normal diverse traffic
- Low entropy = few outcomes dominate = DDoS (all traffic to one target)
- Formula: H(X) = -Σ p(x) log₂ p(x)
- This is the basis of my Contribution 2, following Nychis et al. (2008).

**4. Sequential change detection (CUSUM):**
- Designed to detect when a process changes from one distribution to another
- Does not require knowing when the change will occur
- Optimal for detecting DDoS onset (slow ramp-up attacks)
- This is the other half of my Contribution 2, following Blazek et al. (2001).

---

## Why Statistical Methods, Not ML

Chandola et al. identify the following advantages of statistical over ML approaches:
1. **Interpretability:** A threshold breach is explainable. A neural network output is not.
2. **No training data required:** Statistical baselines adapt from live normal traffic.
3. **Robustness:** ML models can be evaded by adversarial examples. Statistical tests are harder to fool.
4. **Computational simplicity:** CUSUM and entropy run in O(1) per observation. Neural networks require GPU inference.

These four advantages directly justify my decision not to use ML.

---

## Key Formula I Use

**Shannon Entropy for DDoS detection:**
```
H(t) = -Σ_{i} p_i(t) × log₂(p_i(t))

where p_i(t) = requests to service i / total requests in window t

Alert condition: H(t) < θ_H = (1 - α) × H_baseline
where α = sensitivity parameter (I use α = 0.4, i.e., 40% drop)
```

**CUSUM for slow-ramp attacks:**
```
S(0) = 0
S(t) = max(0, S(t-1) + (x(t) - μ₀) - k)

where x(t) = observed request rate at time t
      μ₀   = baseline mean request rate
      k    = allowance parameter (half the expected shift)

Alert condition: S(t) > h (threshold h determined from baseline)
```
