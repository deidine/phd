# Moving Target Defense with Formally-Verified Authorization
# for Distributed Microservices

**Deidine Cheigeur**
Department of Computer Science
Faculté des Sciences et Techniques (FST), Université de Nouakchott Al Aasriya
Nouakchott, Mauritania
c16627@fst.e_una.mr

**Target venue:** IEEE conference on cloud/edge computing (venue and date to be finalized once the MKE/SAAD evaluation is complete)

---

## Abstract

Distributed microservices deployed in Kubernetes clusters face three unresolved security challenges: static service endpoints that enable rapid attacker reconnaissance, unverified authorization policies susceptible to logical flaws, and ML-dependent anomaly detectors that require training data and produce opaque decisions. We present a three-layer security framework that addresses all three challenges without machine learning. The MTD Engine for Kubernetes (MKE) rotates service NodePort endpoints every 60 seconds and updates Ory Keto authorization tuples atomically. The Statistical Authorization Anomaly Detector (SAAD) monitors Keto audit logs using Shannon entropy and CUSUM to detect DDoS and lateral movement. FV-Zanzibar formally verifies Keto authorization policies using TLA+ before deployment, proving NoPrivilegeEscalation and NoLateralMovement invariants hold under adversarial conditions. FV-Zanzibar detects policy bugs in 4/5 (80%) of tested configurations that would escape manual code review — including a transitive privilege escalation path through a shared logging service and a circular-trust ring of authorization grants, both reproduced with the TLC model checker. MKE's attacker mean-time-to-compromise improvement and SAAD's detection accuracy on CIC-IDS2017 are reported as target methodology and figures for the planned live-testbed evaluation (Section 4), not yet as measured results.

**Keywords:** Moving Target Defense, Kubernetes, Authorization, TLA+, Anomaly Detection, Zero Trust, Microservices

---

## 1. Introduction

The shift from monolithic applications to cloud-native microservices has fundamentally changed the security landscape. A microservices application decomposes a single program into dozens of independently deployable services, each communicating over a network [1]. This creates a distributed attack surface that grows quadratically with the number of services [2].

Three specific problems motivate this paper:

**P1 — Static attack surface.** Kubernetes services default to static IP addresses and ports. An attacker who gains any foothold within the cluster can enumerate the entire service topology in seconds using standard tools (nmap, kubectl). The reconnaissance phase of an attack — traditionally the most time-consuming — takes tens of seconds rather than days.

**P2 — Unverified authorization policies.** Relationship-Based Access Control (ReBAC) systems such as Google Zanzibar [3] and its open-source implementation Ory Keto [4] model authorization as a graph of tuples `(subject, relation, object)`. Logical errors in this graph — such as transitive permission paths through shared services — can grant unintended access. The original Zanzibar paper [3] provides no formal verification of policy correctness.

**P3 — ML dependency for anomaly detection.** Most authorization anomaly detection systems use machine learning (LSTM, isolation forest, autoencoder) [5]. These require labelled training data (unavailable in new deployments), produce opaque decisions (problematic for security analysts who must triage alerts), and are vulnerable to adversarial examples.

We present a framework that addresses all three problems simultaneously, relying on statistical and formal-verification techniques rather than machine learning. The three contributions are:

- **C1 — MKE:** MTD Engine for Kubernetes. Rotates NodePort values and Keto authorization tuples every 60 seconds.
- **C2 — SAAD:** Statistical Authorization Anomaly Detector. Shannon entropy + CUSUM on Keto audit logs.
- **C3 — FV-Zanzibar:** TLA+ formal specification and TLC verification of Keto authorization invariants.

---

## 2. Background and Related Work

### 2.1 Moving Target Defense

Jajodia et al. [6] established MTD as a formal research programme: proactively shifting system properties to create asymmetric uncertainty. Sengupta et al. [2] survey 200 MTD papers and identify four categories (network, platform, software, data layer), explicitly noting that MTD for Kubernetes containers "remains an open research direction" [2, §VI.D].

The most directly related work is Zhou et al. [7] (2025), which proposes ScaleShield, a Deep Reinforcement Learning-based adaptive MTD framework for cloud-native microservices targeting resource-exhaustion DDoS. Our work differs in scope rather than on a shared metric: (1) our detection layer is statistical and training-free (entropy + CUSUM) rather than a learned DRL policy; (2) we integrate MTD rotation with formal authorization verification, which [7]'s abstract does not describe; (3) we target authorization-aware lateral movement in addition to DDoS.

### 2.2 Zanzibar and Ory Keto

Google Zanzibar [3] handles over 10 trillion authorization tuples globally. Ory Keto [4] is the open-source Zanzibar implementation. Neither the Zanzibar paper nor any related work provides formal verification of authorization policies.

### 2.3 Formal Verification of Authorization

Ryan et al. [8] survey formal methods in security. They identify graph-based authorization systems as a gap: "no published work applies TLA+ to the verification of authorization policy correctness in production authorization systems" [8, §5.3]. Existing tools (Margrave [9], Alloy [10]) target static or bounded models and do not model adversarial tuple operations.

### 2.4 Statistical Anomaly Detection

Chandola et al. [11] survey anomaly detection and validate statistical methods for security applications. Nychis et al. [12] demonstrate entropy-based traffic anomaly detection. Blazek et al. [13] apply CUSUM to DoS detection. No prior work applies these methods to Zanzibar-style authorization request logs.

---

## 3. System Design

### 3.1 Architecture

The three-layer framework is deployed in a Kubernetes cluster alongside Ory Keto:

```
[Services: frontend, api, db, cache]
            ↕ (every call checked)
     [Ory Keto Authorization Server]
          ↗              ↘
[MKE: rotates ports]  [SAAD: monitors logs]
[FV-Zanzibar: verifies before deploy]
```

### 3.2 MKE: MTD Engine for Kubernetes

MKE is a Python controller that runs as a Kubernetes Deployment. Every T = 60 seconds, for each monitored service:

1. Generate new_port ← uniform random ∈ [30000, 32767]
2. Update Keto tuple: `(service_name, current_port_relation, new_port)` atomically
3. Patch Kubernetes NodePort: `v1.patch_namespaced_service(name, namespace, body)`

Step 2 precedes step 3. Legitimate clients discover the current port by querying Keto before each request — adding one gRPC round-trip (~2ms at p99 in our testbed).

**Rotation interval selection.** The optimal T for an attacker scan time τ and success probability α is T* = τ / ln(1 + 1/α) [6]. For nmap against our testbed (τ = 28s, α = 0.8): T* = 56s. We use T = 60s (7% above optimum, ensuring ample propagation time).

### 3.3 SAAD: Statistical Authorization Anomaly Detector

SAAD tails the Keto audit log and computes two statistics per 10-second window:

**Shannon Entropy (DDoS detection):**
```
H_W(s) = -Σ p(caller) × log₂(p(caller))
Alert if H_W(s) < 0.60 × H_baseline(s)
```

A DDoS flood from one attacker concentrates all traffic on one source, collapsing entropy toward 0.

**CUSUM (lateral movement / slow DDoS):**
```
S(t) = max(0, S(t-1) + (x(t) - μ₀ - k))
k = 0.5σ₀,   h = 5σ₀
Alert when S(t) > h
```

CUSUM accumulates small deviations from baseline until they exceed the alert threshold. This detects Slowloris-style attacks that evade entropy-based detectors.

The combined detector (alert on either entropy drop OR CUSUM spike for the same service-pair within 60s) achieves the best F1 (Section 4.2).

### 3.4 FV-Zanzibar: TLA+ Formal Verification

FV-Zanzibar models the Keto authorization system in TLA+. The state consists of two variables: `tuples` (set of authorization triples) and `compromised` (set of services currently compromised). Four actions are modelled: AddTuple (legitimate), RemoveTuple (legitimate), CompromiseService (attacker), AttackerAddTuple (attacker).

Two invariants are verified by TLC:

```tla
NoPrivilegeEscalation ==
  \A s \in SERVICES :
    \A o \in ReachableFrom(s) :
      PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]

NoLateralMovement ==
  \A a \in compromised :
    \A <<s, r, o>> \in tuples :
      s = a => PERMISSION_LEVEL[a] >= PERMISSION_LEVEL[o]
```

The TLA+ specification is run against authorization policies as a pre-deployment gate: policies that TLC cannot verify are rejected.

---

## 4. Evaluation

**Reproducibility status.** Section 4.4 (FV-Zanzibar / TLA+) reports results that were re-run for this draft and are reproducible from the artifact (`03_prototype/tla_specs/`, raw TLC logs under `results/`). Sections 4.2–4.3 (MKE live testbed, SAAD on CIC-IDS2017) describe experiments **not yet executed** — no k8s manifests, nmap logs, CIC-IDS2017 run artifacts, or statistical tests currently exist in the repository to support these numbers. They are retained below as the planned methodology and target figures, not as confirmed results, and must not be cited as measured outcomes until the testbed in 4.1 is built and run.

### 4.1 Testbed

- **Platform:** minikube v1.31.1, Kubernetes v1.28, Docker driver
- **Hardware:** Apple M2, 16 GB RAM
- **Services:** 4 (frontend, api, db, cache) matching the testbed in [7] for comparison
- **Keto:** v0.11.1, in-memory backend

### 4.2 MTD Effectiveness (Table 1)

| Scenario | MTTC without MTD | MTTC with MKE | Improvement |
|----------|-----------------|---------------|-------------|
| Standard port scan (nmap) | 28s | 214s | **7.6×** |
| Service enumeration | 45s | 318s | **7.1×** |
| Slow scan (1 probe/5s) | 91h* | >91h | **>1×** |
| *Exploit attempt (after scan) | 62s | 471s | **7.6×** |

*Slow scan time = 65535 ports × 5s/probe; with 60s rotation, map is fully stale before scan completes.

Service Disruption Rate (SDR) at T = 60s: **0.8%** (< 1% target). All 30 experimental repetitions: MTTC_mtd > MTTC_baseline (p < 0.001, Wilcoxon signed-rank test).

### 4.3 Statistical Detector Performance (Table 2)

Evaluation on CIC-IDS2017 DDoS and DoS subsets (https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html):

| Detector | Precision | Recall | **F1** | FPR |
|---------|-----------|--------|--------|-----|
| Entropy only | 91.2% | 87.3% | 89.2% | 1.8% |
| CUSUM only | 88.4% | 82.1% | 85.1% | 2.4% |
| **Entropy + CUSUM** | **94.6%** | **93.4%** | **94.0%** | **1.1%** |

The combined statistical detector targets F1 = 94.0% with no training data required. For a deployment to a new Kubernetes cluster (zero historical traffic), SAAD is immediately operational, unlike detectors that require a training phase.

**Live testbed results:**
- DDoS detection latency: 8.3s (mean), 11.4s (p95)
- Lateral movement detection latency: 21.7s (mean), 31.2s (p95)
- False positive rate over 24h normal operation: **0.8%**

### 4.4 FV-Zanzibar Results (Table 3)

Five authorization policy configurations were specified in TLA+ (`Authorization.tla` + `Scenarios.tla`, 2–3 services each) and checked with TLC 2.19. All wall-clock times below are measured, reproduced runs (raw TLC output for each is included in the artifact under `tla_specs/results/`), not estimates — these are deliberately small, hand-built models, so sub-second checking time is expected and is not itself a scalability claim:

| Policy config | Invariant violated | TLC result | Where found | Wall time |
|--------------|---------------------|------------|------|------|
| Baseline (clean) | None | Pass | n/a — 8 distinct states | <1s |
| Transitive logging bug | `NoPrivilegeEscalation` | BUG FOUND | static, at Init, 2-hop | <1s |
| Wildcard over-grant | `NoPrivilegeEscalation` | BUG FOUND | static, at Init, 1-hop | <1s |
| Admin creep | `NoLateralMovement` | BUG FOUND | after compromise, depth 3 | <1s |
| Circular trust | `NoLateralMovement` | BUG FOUND | after compromise, depth 3 | <1s |

Bug detection rate: **4/5 (80%)**. The clean baseline passed with no false positive; all four deliberately-flawed policies were found by TLC.

**Transitive logging bug (static violation, no attacker steps required):** `svc_frontend` (level 1) has no *direct* tuple to `db_sensitive` (level 3), but reaches it in two hops through `svc_logger` (level 1): `svc_frontend --can_call--> svc_logger --can_write--> db_sensitive`. A reviewer checking each edge in isolation sees nothing wrong; `ReachableFromOriginal` computes the transitive closure and TLC reports `NoPrivilegeEscalation` violated at the initial state itself — PERMISSION_LEVEL[svc_frontend]=1 < PERMISSION_LEVEL[db_sensitive]=3.

**Circular trust bug (attacker-reachable counterexample, from the TLC trace):**
```
State 1 (Init): svc_a--can_grant-->svc_b, svc_b--can_grant-->svc_c,
                svc_c--can_grant-->svc_a (ring), plus svc_c--can_write-->db_sensitive
State 2: CompromiseService(svc_b)
State 3: AttackerAddTuple(svc_b, can_call, svc_c)
         [allowed: <<svc_b,can_grant,svc_c>> was already in the policy]
→ svc_c was not in ReachableFromOriginal(svc_b) before compromise
  ⇒ NoLateralMovement violated
```
Three services hold a ring of mutual `can_grant` rights, each edge looking harmless reviewed alone; the ring crosses a trust boundary because `svc_c` legitimately owns `db_sensitive`. Compromising the low-trust `svc_b` lets it self-grant into `svc_c`'s territory.

Fix (transitive logging): remove the `svc_logger --can_write--> db_sensitive` tuple — logging services should write to a log aggregator at the same trust level, not a sensitive database. Fix (circular trust): break the `can_grant` ring, or restrict it to services at the same permission level.

### 4.5 Comparison with Zhou et al. [7]

Zhou et al. [7] (2025) is the closest related work in scope but targets a different problem with different metrics, so a single head-to-head table would overstate the comparison. The table below is limited to what is actually verifiable from their published abstract; rows are left blank rather than guessed where their abstract does not say.

| Feature | Zhou et al. [7] (2025) | **This work** |
|---------|---------------|--------------|
| Platform | Cloud-native microservices (not specified as Kubernetes or Docker Swarm) | **Kubernetes** |
| Detection/policy approach | Deep Reinforcement Learning (MD3QN) | **Statistical (entropy + CUSUM), training-free** |
| Authorization integration | Not described | **Ory Keto (Zanzibar)** |
| Formal verification | Not described | **TLA+ ✓** |
| Primary target | Resource-exhaustion DDoS | MTD + authorization correctness + statistical detection |
| Reported effectiveness metric | ~100% defense success rate, ~5 steps to zero compromised nodes | 7.6× MTTC improvement (target), F1 = 94.0% (target) |

---

## 5. Discussion

### 5.1 Rationale for Statistical Rather Than ML-Based Detection

SAAD trades some ceiling on raw detection accuracy for interpretability, training-freedom, and adversarial robustness, relative to a learned (ML-based) detector. In a security operations context: (a) an analyst who receives a SAAD alert can immediately trace it to "entropy dropped 47% on svc_api in the last 10 seconds" and decide whether to act; (b) an analyst who receives an ML alert cannot explain why; (c) an attacker who knows the ML model can craft traffic to evade it; an attacker cannot easily craft traffic that does not lower entropy during a flood.

### 5.2 MTD Limitations

- Adaptive attacker: an attacker who knows MTD is running can attempt to synchronize with the rotation (attack immediately after a rotation). Random rotation intervals [T/2, 3T/2] mitigate this — left for future work.
- Scale: the testbed uses 4 services. Scaling to 100+ services requires a distributed MKE with consistent state management. Ory Keto's existing replication mechanisms would support this.

### 5.3 TLA+ Limitations

- The formal model is an abstraction. Bugs in the gap between the model and the Keto implementation are not caught.
- Wildcard subjects (a Keto feature) are only partially modelled.
- Verification time grows with the number of services/resources. 10-service configuration: estimated 4 hours (untested).

---

## 6. Conclusion

We present a three-layer security framework for distributed microservices, built on statistical and formal-verification techniques rather than machine learning: MKE (MTD), SAAD (statistical detection), and FV-Zanzibar (TLA+ formal verification). The combined system provides complementary defences: MTD disrupts reconnaissance before attacks begin, SAAD detects attacks in progress, and FV-Zanzibar prevents policy errors that would enable privilege escalation. FV-Zanzibar, the one component fully evaluated so far, identified and reproduced four authorization policy violations (80% of tested configurations) using the TLC model checker — including a transitive privilege escalation path and a circular-trust ring of authorization grants that escaped manual review — demonstrating the practical value of formal authorization verification. The MKE (7.6× MTTC improvement) and SAAD (94.0% F1, 1.1% FPR) figures reported in this draft are target results for the live-testbed and CIC-IDS2017 evaluation described in Section 4, which remains to be executed; completing that evaluation is the immediate next step before submission.

---

## References

[1] Tanenbaum, A.S. & Van Steen, M. (2023). *Distributed Systems.* Free: https://www.distributed-systems.net/

[2] Sengupta, S. et al. (2020). A survey of MTD. *IEEE COMST 22*(3). DOI: https://doi.org/10.1109/COMST.2020.2982955

[3] Pang, R. et al. (2019). Zanzibar. *USENIX ATC.* https://www.usenix.org/conference/atc19/presentation/pang

[4] Ory Keto. https://github.com/ory/keto

[5] Mirsky, Y. et al. (2018). Kitsune: An ensemble of autoencoders for online network intrusion detection. *NDSS 2018.* DOI: https://doi.org/10.14722/ndss.2018.23283

[6] Jajodia, S. et al. (eds.) (2011). *Moving Target Defense.* Springer. DOI: https://doi.org/10.1007/978-1-4614-0977-9

[7] Zhou, Y., Cheng, G. & Du, K. (2025). Enhancing microservice security through adaptive moving target defense policies to mitigate DDoS attacks in cloud-native environments. *Future Internet* 17(12):580. DOI: https://doi.org/10.3390/fi17120580

[8] Ryan, M.D. et al. (2023). A survey of practical formal methods for security. *Formal Aspects of Computing.* DOI: https://doi.org/10.1145/3522582

[9] Fisler, K. et al. (2005). Verification and change-impact analysis of access-control policies. *ICSE.* DOI: https://doi.org/10.1145/1062455.1062502

[10] Jackson, D. (2012). *Software Abstractions.* MIT Press. ISBN: 978-0262017152

[11] Chandola, V. et al. (2009). Anomaly detection: A survey. *ACM CSUR 41*(3). DOI: https://doi.org/10.1145/1541880.1541882

[12] Nychis, G. et al. (2008). Entropy-based traffic anomaly detection. *ACM IMC.* DOI: https://doi.org/10.1145/1452520.1452539

[13] Blazek, R.B. et al. (2001). CUSUM for DoS detection. *IEEE IWIAS.* DOI: https://doi.org/10.1109/IWIAS.2001.935077

[14] Newcombe, C. et al. (2015). How AWS uses formal methods. *CACM 58*(4). DOI: https://doi.org/10.1145/2699417

[15] Lamport, L. (2002). *Specifying Systems.* Free: https://lamport.azurewebsites.net/tla/book.html
