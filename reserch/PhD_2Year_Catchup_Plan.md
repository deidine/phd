# PhD 2-Year Catchup Plan
## Field: Cybersecurity + Distributed Systems (No Machine Learning)
## Approach: Moving Target Defense · Statistical Detection · Formal Verification · Zanzibar

---

## Your Thesis in One Line

> Secure distributed microservices against network attacks using
> Moving Target Defense, statistical anomaly detection, and formally-verified
> Zanzibar/Keto authorization — zero machine learning.

---

## What You Will Produce in 6 Months

| Deliverable | Month |
|-------------|-------|
| 25 papers read, 1-page summary each | 2 |
| Literature review (30 pages) | 2 |
| Thesis Chapters 1 & 2 | 3 |
| Working prototype (Python + Kubernetes) | 3 |
| Thesis Chapter 3 (Methodology) | 4 |
| Conference paper submitted | 4 |
| Thesis Chapter 4 (Results) | 5 |
| Journal paper submitted | 6 |

---

## Phase 1 — Read 25 Papers (Weeks 1–4)
### Write a 1-page summary for EVERY paper. These summaries become Chapter 2.

---

### Tier 1 — Foundations (Week 1): Must-read first

**Paper 1 — Your foundation book chapter (free)**
> Anderson, R. (2020). *Security Engineering*, Ch. 4, 7, 13, 21, 26. Wiley.
> 🔗 https://www.cl.cam.ac.uk/~rja14/book.html
> Read chapters 4, 7, and 13 this week. Takes ~4 hours. No skipping.

**Paper 2 — Distributed systems foundation**
> Tanenbaum, A. S., & Van Steen, M. (2023). *Distributed Systems*, Ch. 1–5. 4th ed.
> 🔗 https://www.distributed-systems.net/
> Read chapters 1 and 2 this week. Understand what a distributed system is cold.

**Paper 3 — Zanzibar (your authorization platform)**
> Pang et al. (2019). Zanzibar: Google's Consistent, Global Authorization System.
> *USENIX ATC*.
> 🔗 https://www.usenix.org/conference/atc19/presentation/pang
> This is the paper behind Ory Keto. Read it fully. Take notes on the tuple model.

**Paper 4 — How AWS uses formal methods (your justification for TLA+)**
> Newcombe et al. (2015). How Amazon Web Services Uses Formal Methods.
> *Communications of the ACM*, 58(4), 66–73.
> 🔗 https://cacm.acm.org/magazines/2015/4/184701
> Short paper (~7 pages). Read in one sitting.

**Paper 5 — Access control survey**
> Sandhu, R., & Samarati, P. (1994). Access Control: Principles and Practice.
> *IEEE Communications Magazine*, 32(9), 40–48.
> Classic paper (~700 citations). Defines ACL, RBAC, MAC — vocabulary you must know.

---

### Tier 2 — Moving Target Defense (Week 2): 7 papers

**Paper 6 — The MTD survey (your main MTD reference)**
> Sengupta, S., et al. (2020). A Survey of Moving Target Defenses for Network Security.
> *IEEE Communications Surveys & Tutorials*, 22(3), 1909–1941.
> 🔗 https://doi.org/10.1109/COMST.2020.2982955
> Read sections 1–4. This maps the entire MTD field.

**Paper 7 — MTD original concept**
> Jajodia, S., et al. (2011). Moving Target Defense: Creating Asymmetric Uncertainty
> for Cyber Threats. Springer.
> The book that coined "Moving Target Defense" as a research direction.
> Read Chapter 1 (free preview on Google Books).

**Paper 8 — MTD for cloud-based systems**
> MTD CBITS: Moving Target Defense for Cloud-Based IT Systems.
> 🔗 https://www.researchgate.net/publication/319072448
> Closest existing work to your Contribution 1. Know its limitations.

**Paper 9 — MTD for microservices (2024)**
> Enhancing Microservice Security Through Adaptive MTD Policies to Mitigate DDoS
> in Cloud-Native Environments. *Future Internet*, MDPI, 2024.
> 🔗 https://www.mdpi.com/1999-5903/17/12/580
> Direct competitor. Understand exactly what it does and does NOT do
> (it does not integrate authorization, it does not use formal verification).

**Paper 10 — MTD for Kubernetes (2025)**
> ADA: Automated Moving Target Defense for AI Workloads via Ephemeral
> Infrastructure-Native Rotation in Kubernetes. arXiv:2505.23805.
> 🔗 https://arxiv.org/html/2505.23805
> Very recent. Read to ensure your MTD approach is differentiated.

**Paper 11 — IP hopping / address mutation MTD**
> Jafarian, J. H., et al. (2012). OpenFlow Random Host Mutation: Transparent
> Moving Target Defense Using Software Defined Networking.
> *HotSDN*, pp. 127–132.
> Classic network-layer MTD paper. Understand the IP hopping mechanism.

**Paper 12 — MTD evaluation framework**
> Zhuang, R., et al. (2014). Towards a Theory of Moving Target Defense.
> *MTD Workshop at CCS*.
> Defines how to MEASURE the effectiveness of MTD — your Chapter 4 metrics.

---

### Tier 3 — Formal Methods & Verification (Week 3): 7 papers

**Paper 13 — TLA+ introduction (FREE book)**
> Lamport, L. (2002). *Specifying Systems: The TLA+ Language and Tools
> for Hardware and Software Engineers*. Addison-Wesley.
> 🔗 FREE at: https://lamport.azurewebsites.net/tla/book.html
> Read Chapters 1–3 this week. TLA+ is your tool — you must learn it.

**Paper 14 — Formal methods survey for security**
> Ryan, M. D., et al. (2023). A Survey of Practical Formal Methods for Security.
> *Formal Aspects of Computing* (ACM).
> 🔗 https://dl.acm.org/doi/full/10.1145/3522582
> Maps all formal verification tools for security. TLA+ vs. ProVerif vs. others.
> After reading: you know why TLA+ is the right choice for your work.

**Paper 15 — ProVerif for security protocols**
> Blanchet, B. (2022). Formal Verification of Security Protocols: ProVerif
> and Extensions. *Springer*.
> 🔗 https://link.springer.com/chapter/10.1007/978-3-031-06788-4_42
> ProVerif is the alternative to TLA+. Read to understand why you chose TLA+ instead
> (TLA+ is better for distributed system invariants, ProVerif for protocol messages).

**Paper 16 — TLA+ for distributed systems**
> Lamport, L. (2019). If You're Not Writing a Program, Don't Use a Programming
> Language. *PLDI Keynote* (video + slides).
> 🔗 Search "Lamport PLDI 2019" on YouTube.
> Short but important — Lamport argues TLA+ is perfect for distributed system specs.

**Paper 17 — Formal access control verification**
> Koch, M., et al. (2005). MAC and DAC Policy Specification and Validation
> Using UML and OCL. *SACMAT*.
> Formal verification of access control policies — background for Contribution 3.

**Paper 18 — Privilege escalation detection**
> Haber, M., & Hibbert, B. (2018). *Privileged Attack Vectors*. Apress.
> Chapter 5: Privilege Escalation in Distributed Systems.
> Defines the exact attacks your formal invariants must block.

**Paper 19 — Lateral movement in distributed systems**
> Alsaheel, A., et al. (2021). ATLAS: A Sequence-based Learning Approach for
> Attack Investigation. *USENIX Security*.
> Describes how lateral movement works step by step.
> You need to understand the attack to formally model blocking it.

---

### Tier 4 — Distributed Security & Attacks (Week 4): 6 papers

**Paper 20 — Network attack taxonomy**
> Hoque, N., et al. (2017). Network Attacks: Taxonomy, Tools and Systems.
> *Journal of Network and Computer Applications*, 40, 307–324.
> Defines DDoS, MITM, port scanning, lateral movement. Your Chapter 2 uses this.

**Paper 21 — DDoS in cloud/SDN**
> Yan, Q., et al. (2016). SDN and DDoS Attacks in Cloud Computing: A Survey.
> *IEEE Communications Surveys & Tutorials*, 18(1), 602–622.
> ~1000 citations. Background on DDoS in your target environment.

**Paper 22 — Statistical anomaly detection (no ML)**
> Chandola, V., et al. (2009). Anomaly Detection: A Survey.
> *ACM Computing Surveys*, 41(3), 15.
> ~8000 citations. The foundational survey on anomaly detection.
> Read Section 3 (statistical methods) carefully — this is your Contribution 2.

**Paper 23 — CUSUM for network anomaly detection**
> Blazek, R. B., et al. (2001). A Novel Approach to Detection of DoS Attacks
> via Adaptive Sequential and Batch-Sequential Change Point Detection Methods.
> *IEEE Workshop on Information Assurance*.
> Introduces CUSUM for network attack detection. Your Contribution 2 builds on this.

**Paper 24 — Entropy-based detection**
> Nychis, G., et al. (2008). An Empirical Evaluation of Entropy-based Traffic
> Anomaly Detection. *IMC*.
> Proves entropy drops sharply during DDoS attacks. Your statistical baseline.

**Paper 25 — Zero Trust architecture**
> NIST SP 800-207 (2020). Zero Trust Architecture.
> 🔗 https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf
> The US government standard for zero-trust security — your architectural reference.
> Free, authoritative, essential reading.

---

## Phase 2 — Write Chapters 1 & 2 (Weeks 5–8)

### Chapter 1 — Introduction (15 pages) — 2 pages/day

```
1.1  Motivation (3 pages)
     - Microservices are everywhere — and vulnerable
     - Real attacks: SolarWinds (lateral movement), Capital One (privilege escalation)
     - Why static systems are easy to attack

1.2  Problem Statement (2 pages)
     - Three unsolved problems:
       P1: Static endpoints enable attacker reconnaissance
       P2: Authorization policies have undetected logical flaws
       P3: Anomaly detection requires ML (fragile, opaque)

1.3  Research Questions (1 page)
     - RQ1: Does MTD endpoint rotation prevent lateral movement in Kubernetes?
     - RQ2: Can CUSUM + entropy detect DDoS without ML at < 1% false positive rate?
     - RQ3: Can TLA+ prove Zanzibar policies free of privilege escalation paths?

1.4  Contributions (1 page) — three bullet points

1.5  Scope & Limitations (1 page)

1.6  Thesis Structure (1 page)
```

### Chapter 2 — Literature Review (30 pages) — 2 pages/day

```
2.1  Distributed Systems Architecture (4 pages)
     Papers: Tanenbaum & Van Steen, Anderson

2.2  Access Control Models (4 pages)
     Papers: Sandhu & Samarati, Zanzibar/Pang, NIST 800-207

2.3  Moving Target Defense (6 pages)
     Papers: Sengupta, Jajodia, MTD CBITS, MDPI 2024, ADA 2025

2.4  Formal Verification of Distributed Systems (6 pages)
     Papers: Lamport TLA+, Ryan survey, ProVerif, AWS/Newcombe

2.5  Statistical Anomaly Detection (4 pages)
     Papers: Chandola, Blazek (CUSUM), Nychis (entropy)

2.6  Network Attacks in Distributed Systems (4 pages)
     Papers: Hoque taxonomy, Yan DDoS, ATLAS lateral movement

2.7  Research Gaps (2 pages)  ← The most important section
     Gap 1: No MTD + Zanzibar integration
     Gap 2: No formal verification of Keto/Zanzibar policies
     Gap 3: No statistical (non-ML) IDS for microservices with auth layer
```

---

## Phase 3 — Build Prototype (Weeks 9–12)

### Sprint 1 (Week 9) — Kubernetes testbed
```bash
# Install minikube
brew install minikube && minikube start

# Install Ory Keto
helm repo add ory https://k8s.ory.sh/helm/charts
helm install keto ory/keto

# Deploy 3 test microservices (frontend → api → database)
kubectl apply -f demo-services.yaml
```

### Sprint 2 (Week 10) — MTD engine
- Python Kubernetes controller (uses `kubernetes` Python library)
- Every 60 seconds: rotate service ClusterIPs and port assignments
- Service discovery via Keto relationship tuples (not hardcoded IPs)
- Measure: how long does an attacker take to re-map the system?

### Sprint 3 (Week 11) — Statistical detector
- Capture Keto authorization request logs
- Compute Shannon entropy of request distribution per service pair
- Apply CUSUM to per-service request rate
- Threshold alert: entropy drop > 40% OR CUSUM exceeds 3σ
- No training data needed — baselines computed from first 10 minutes of normal traffic

### Sprint 4 (Week 12) — TLA+ formal model
- Model Keto authorization tuple graph in TLA+
- Define invariant 1: `NoPrivilegeEscalation` — no subject reaches resources above their level
- Define invariant 2: `NoLateralMovement` — compromised service cannot self-authorize
- Run TLC model checker — proof or counterexample
- Document any policy flaws found

---

## Phase 4 — Chapters 3–4 + Conference Paper (Weeks 13–20)

### Chapter 3 — Methodology (20 pages)

```
3.1  System Architecture — diagram of all three components
3.2  Threat Model — attacker capabilities and goals
3.3  MTD Engine Design — algorithm, rotation period analysis
3.4  Statistical Detector Design — entropy + CUSUM formulas
3.5  TLA+ Specification — excerpt of the formal model
3.6  Evaluation Setup — testbed, attack scenarios, metrics
```

### Chapter 4 — Results (25 pages)

```
4.1  MTD Effectiveness — attacker mean-time-to-exploit with/without MTD
4.2  Statistical Detector Results — precision, recall, false positive rate
4.3  TLA+ Verification Results — proved invariants or found bugs
4.4  Combined System — does MTD + detection + verified auth stop all three attack types?
4.5  Performance Overhead — what does this cost in CPU/memory/latency?
```

### Conference Paper Target (Month 4)

**Title:** "Moving Target Defense with Formally-Verified Authorization for Distributed Microservices"

| Venue | Deadline | Pages |
|-------|----------|-------|
| IEEE CLOUD | April | 8 |
| ACM CODASPY | October | 6 |
| ESORICS Workshop | May | 6 |
| IEEE CNS (Communications & Network Security) | May | 6 |

---

## Phase 5 — Chapters 5–6 + Journal (Weeks 21–26)

### Chapter 5 — Discussion (10 pages)
- What attacks does MTD NOT stop?
- Formal verification limitations (state space explosion)
- Deployment considerations for real cloud providers (AWS, GCP, Azure)
- Future work: extend to serverless, extend formal model to cover timing attacks

### Chapter 6 — Conclusion (5 pages)

### Journal Paper

| Journal | Impact Factor | Scope |
|---------|--------------|-------|
| *IEEE Transactions on Dependable and Secure Computing* | 7.3 | Perfect fit |
| *Computers & Security* (Elsevier) | 5.6 | Broad security |
| *Journal of Computer Security* (IOS Press) | 2.2 | Formal methods + security |

---

## Your Elevator Pitch (Memorise This — No ML, No SCADA, No OT)

> "My thesis secures **distributed microservices** in the cloud using
> three techniques — no machine learning.
> First, **Moving Target Defense**: I rotate service endpoints in Kubernetes
> so attackers cannot map the system.
> Second, **statistical detection** using entropy and CUSUM to catch
> DDoS and abnormal authorization patterns — pure mathematics.
> Third, **formal verification** with TLA+ to prove that the
> Zanzibar-based authorization model cannot be exploited for
> privilege escalation or lateral movement.
> The gap is confirmed by a 2020 IEEE MTD survey and by the fact that
> Zanzibar itself (Google's paper, USENIX 2019) has never been formally verified."

---

## Tools to Install This Week

```bash
# Kubernetes
brew install minikube kubectl helm
minikube start --driver=docker

# Ory Keto
helm repo add ory https://k8s.ory.sh/helm/charts
helm install keto ory/keto

# Python
pip install kubernetes numpy scipy matplotlib pandas

# TLA+ (formal verification)
# Download TLA+ Toolbox (GUI): https://lamport.azurewebsites.net/tla/toolbox.html
# Or VS Code extension: search "TLA+ Nightly" in VS Code extensions

# Paper manager
# Download Zotero: https://www.zotero.org/
```

---

## "Sound Like a 2nd Year" Checklist

Practice saying each answer in under 2 minutes:

- [ ] What is a distributed system? What are its main challenges?
- [ ] What is a microservice? How is it different from a monolith?
- [ ] What is Kubernetes? What is a pod, a service, a namespace?
- [ ] What is Zanzibar? What is Ory Keto?
- [ ] What is relationship-based access control (ReBAC)?
- [ ] What is Moving Target Defense? Give an example.
- [ ] What is TLA+? What does a model checker do?
- [ ] What is CUSUM? What is Shannon entropy?
- [ ] What is privilege escalation? What is lateral movement?
- [ ] What are your three research contributions?
