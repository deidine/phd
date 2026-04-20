# Chapter 3 — Methodology

**Thesis:** Moving Target Defense and Formal Authorization Verification
for Securing Distributed Microservices Against Network Attacks

**Author:** Deidine Cheigeur | PhD in Computer Science | 2026

---

## 3.1 System Architecture Overview

This chapter describes the design, implementation, and evaluation methodology of the three-layer security framework proposed in this thesis. The framework targets distributed microservices deployed in a Kubernetes cluster and provides defence against network reconnaissance, DDoS attacks, lateral movement, and authorization policy flaws.

### 3.1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                           │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  svc_frontend │    │   svc_api    │    │   svc_db     │      │
│  │  NodePort:??? │    │  NodePort:???│    │  ClusterIP   │      │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘      │
│         │                   │                                    │
│         │  Every request goes through Keto (authorization)      │
│         ▼                   ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Ory Keto Authorization Server               │   │
│  │   Tuples: {(svc_frontend, can_call, svc_api), ...}      │   │
│  │   Audit log: /var/log/keto/access.log                   │   │
│  └────────────┬────────────────────┬───────────────────────┘   │
│               │                    │                            │
│               ▼                    ▼                            │
│  ┌────────────────────┐  ┌────────────────────────────────┐   │
│  │  Layer 1: MKE      │  │  Layer 2: SAAD                 │   │
│  │  MTD Controller    │  │  Statistical Detector          │   │
│  │  - Rotates ports   │  │  - Reads Keto audit log        │   │
│  │  - Updates Keto    │  │  - Shannon entropy per service │   │
│  │  - 60s interval    │  │  - CUSUM per service-pair      │   │
│  └────────────────────┘  └────────────────────────────────┘   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Layer 3: FV-Zanzibar                                     │  │
│  │  TLA+ Authorization.tla — run BEFORE policy deployment    │  │
│  │  TLC checks: NoPrivilegeEscalation, NoLateralMovement     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1.2 Layer Interaction

The three layers operate at different phases of the security lifecycle:

- **FV-Zanzibar (Layer 3)** operates at policy deployment time (offline). Before any authorization policy is deployed to Keto, it is checked by TLC. If TLC finds a violation, the policy is rejected.
- **MKE (Layer 1)** operates continuously at runtime. It rotates service endpoints every 60 seconds and updates Keto authorization tuples to reflect the new endpoints.
- **SAAD (Layer 2)** operates continuously at runtime. It tails the Keto audit log and raises alerts when statistical anomalies indicate DDoS or lateral movement.

The layers are complementary: FV-Zanzibar prevents logical authorization bugs; MKE disrupts network reconnaissance and exploitation; SAAD detects attacks that bypass MTD (e.g., an attacker who discovers the new port before the next rotation).

---

## 3.2 Threat Model

### 3.2.1 Attacker Capabilities

The threat model follows the Dolev-Yao adversary model (Dolev & Yao, 1983) adapted for cloud-native environments. The attacker:

1. **Can observe all network traffic** within the cluster (achieved via a compromised pod or traffic mirroring)
2. **Can send arbitrary requests** to any observable service endpoint
3. **Can compromise individual services** (but not the control plane or Keto)
4. **Cannot break cryptographic primitives** (TLS, JWT signatures)
5. **Cannot modify Keto authorization policies** (policy write requires admin credentials not held by attacker)
6. **Is computationally bounded** (cannot brute-force the 2^16 port space within the MTD rotation interval)

### 3.2.2 Attack Scenarios

Three attack scenarios are modelled, each targeting one or more layers:

**Scenario 1 — DDoS via Port Flood (targets Layer 1 and Layer 2)**
Attacker discovers the current port of a target service (via scanning or cached reconnaissance), then floods that port with requests. Counter-measure: MKE rotates the port every 60s, invalidating the attacker's map. SAAD detects the flood via entropy drop.

**Scenario 2 — Lateral Movement (targets Layers 2 and 3)**
Attacker compromises svc_frontend and attempts to call svc_db directly (bypassing svc_api). Counter-measure: Keto rejects unauthorized calls. SAAD detects the anomalous svc_frontend → svc_db call pattern via CUSUM. FV-Zanzibar ensures no policy configuration can accidentally grant this access.

**Scenario 3 — Slow Reconnaissance (targets Layer 1)**
Attacker conducts a slow port scan (1 probe per 5 seconds) to avoid threshold-based detection. Counter-measure: MKE rotates ports faster (60s) than a full port scan takes (2^16 ports × 5s/probe = 91 hours). By the time the scan completes, all discovered ports are stale.

### 3.2.3 Assets and Trust Boundaries

| Component | Trust Level | Protected by |
|-----------|-------------|--------------|
| Kubernetes control plane | Fully trusted | Kubernetes RBAC (admin only) |
| Ory Keto server | Fully trusted | Network policy (only services can reach Keto) |
| svc_frontend | Untrusted (exposed) | MKE + Keto + SAAD |
| svc_api | Semi-trusted | Keto + SAAD |
| svc_db | Trusted | Keto + SAAD (isolated, no external exposure) |
| Administrator | Fully trusted | Not in scope |

---

## 3.3 Layer 1: MTD Engine for Kubernetes (MKE)

### 3.3.1 Design Rationale

The MTD Engine for Kubernetes (MKE) implements network-layer MTD by rotating the NodePort values of Kubernetes services on a fixed interval. The design decisions are:

**What to rotate:** NodePort values (range 30000–32767). Not IP addresses (stable across pod lifecycle) and not ClusterIP (requires DNS change, high disruption).

**Why NodePort:** NodePort changes are applied atomically by the Kubernetes API server without restarting pods. The change is propagated to all nodes within the kube-proxy sync interval (default: 30s, configured to 1s in the testbed). Legitimate clients discover the new port by querying Keto.

**Rotation interval (T):** 60 seconds. The trade-off between security (shorter T → more frequent rotation → attacker's map stales faster) and disruption (shorter T → more frequent port changes → higher risk of in-flight requests failing) was evaluated empirically (Section 3.3.3). T = 60s achieves SDR < 1% and MTTC increase of 7.2×.

### 3.3.2 MKE Algorithm

```
Algorithm MTD-Rotate(service_name, keto_client, k8s_client):
  1. new_port ← random_int(30000, 32767)
  2. old_port ← get_current_nodeport(k8s_client, service_name)
  3. update_keto_tuple(keto_client, service_name, new_port)
     # Atomic: Keto now serves new_port before Kubernetes applies it
     # Clients querying Keto during the transition get new_port
  4. patch_kubernetes_service(k8s_client, service_name, new_port)
     # Kubernetes propagates change to all nodes (< 1s in testbed)
  5. log(f"Rotated {service_name}: {old_port} → {new_port}")
  6. schedule(MTD-Rotate, delay=T)
```

Step 3 precedes Step 4. This ordering ensures that Keto always reflects the port that Kubernetes will apply, not a stale value. If Step 4 fails (Kubernetes API error), the Keto tuple is rolled back.

### 3.3.3 Client Discovery Protocol

For MKE to be transparent to legitimate clients, clients must discover the current port before each request rather than caching it indefinitely. The protocol:

```python
def call_service(target, operation, payload, keto):
    # 1. Ask Keto for the current endpoint
    port = keto.check(subject=self.name, relation="can_call", 
                      object=target, return_metadata=True)["port"]
    # 2. Execute the request
    response = http.post(f"http://{target}:{port}/{operation}", json=payload)
    return response
```

This adds a Keto lookup per request (one gRPC call, ~2ms latency at 99th percentile in the testbed). The overhead is measurable but acceptable — service mesh data planes (Envoy/Istio) perform similar per-request operations.

**Alternative considered:** In-cluster DNS TTL reduction (set TTL=1s). Rejected because DNS caching in client libraries is inconsistent and many libraries cache indefinitely regardless of TTL. Keto-based discovery is deterministic.

### 3.3.4 MKE Implementation

Full implementation: [03_prototype/mtd_controller/mtd_controller.py](../03_prototype/mtd_controller/mtd_controller.py)

Key dependencies:
```
kubernetes==28.1.0     # Kubernetes Python client
requests==2.31.0       # Keto REST API calls
```

Full requirements: [03_prototype/mtd_controller/requirements.txt](../03_prototype/mtd_controller/requirements.txt)

---

## 3.4 Layer 2: Statistical Authorization Anomaly Detector (SAAD)

### 3.4.1 Input: Keto Authorization Log

SAAD reads the Keto audit log at `/var/log/keto/access.log`. Each log entry records: timestamp, subject, object, relation, check result (allow/deny). The detector does not inspect the *content* of requests — it only observes the *pattern* of authorization checks. This is a deliberate design choice: content inspection requires TLS termination and deep packet inspection, which violate the Zero Trust principle and add significant complexity.

Example log entries:
```
2026-01-15T10:23:11Z, svc_frontend, svc_api, can_call, allow
2026-01-15T10:23:11Z, svc_api, svc_db, can_read, allow
2026-01-15T10:23:12Z, svc_frontend, svc_api, can_call, allow
...
```

During a DDoS attack:
```
2026-01-15T10:25:01Z, attacker_ip, svc_api, can_call, deny
2026-01-15T10:25:01Z, attacker_ip, svc_api, can_call, deny
2026-01-15T10:25:01Z, attacker_ip, svc_api, can_call, deny
... (1,000 entries in the next 1 second)
```

### 3.4.2 Shannon Entropy Detector

For each target service s, within each 10-second window W:

1. Collect the multiset of subjects that made requests to s: {subject₁, subject₂, ...}
2. Compute frequency counts: count[subj] = |{entries where object = s and subject = subj}|
3. Compute Shannon entropy:
   `H_W(s) = -Σ (count[subj] / total) × log₂(count[subj] / total)`

During the baseline period (first 600 seconds = 10 minutes):
- Store the first computed H as `H_baseline(s)`

For subsequent windows:
- Alert if `H_W(s) < 0.60 × H_baseline(s)` (40% drop)
- Otherwise update baseline: `H_baseline(s) ← 0.95 × H_baseline(s) + 0.05 × H_W(s)`

The exponential moving average update (α = 0.95) allows the baseline to track legitimate long-term drift while ignoring short-term anomalies.

### 3.4.3 CUSUM Detector

For each (subject, object) service-pair pair (s→t), SAAD tracks the per-window request rate and runs CUSUM:

**Baseline collection (600s / 10s = 60 windows):**
- Record rates r₁, r₂, ..., r₆₀
- Compute μ₀ = mean(rates), σ₀ = std(rates)
- Set k = 0.5 × σ₀ (CUSUM allowance)
- Set h = 5.0 × σ₀ (alert threshold)

**Per-window update:**
```
S(t) = max(0, S(t-1) + (r(t) - μ₀ - k))
if S(t) > h:
    alert("Lateral movement / slow DDoS on pair {s}→{t}")
    S(t) = 0  # reset
```

Parameter rationale: k = 0.5σ is the classical recommendation (Wald, 1945) for detecting a shift of size 1σ with minimum expected detection delay. h = 5σ gives a mean time between false alarms of 370 windows (61 minutes) under null hypothesis — acceptable for an operational detector.

### 3.4.4 SAAD Implementation

Full implementation: [03_prototype/statistical_detector/detector.py](../03_prototype/statistical_detector/detector.py)

Key design decisions:
- **No ML imports.** The implementation uses only: `math`, `numpy`, `collections`, standard library.
- **Real-time tail mode:** the detector seeks to the end of the log file on startup and processes each new line as it is appended.
- **Sliding window:** window state is cleared after each `tick()` call. This avoids unbounded memory growth.
- **No state persistence:** the detector is stateless across restarts (re-establishes baselines). A future version could persist baseline state to disk.

---

## 3.5 Layer 3: FV-Zanzibar — TLA+ Formal Verification

### 3.5.1 Modelling Approach

FV-Zanzibar models the Keto authorization system as a TLA+ state machine. The central design question was how to model the adversary. Two options were considered:

**Option A (optimistic):** Model only legitimate operations (AddTuple, RemoveTuple). Check safety of the policy structure itself.

**Option B (adversarial):** Model both legitimate operations and adversarial operations (AttackerAddTuple, CompromiseService). Check that no sequence of mixed legitimate + adversarial operations can violate the invariants.

This thesis uses Option B. Option A provides weaker guarantees: it does not cover the scenario where a compromised service tries to modify its own authorization tuples. Option B is strictly stronger: if the invariants hold under adversarial operations, they hold under legitimate operations as well.

### 3.5.2 State Space

The TLA+ model has:
- **Variables:** `tuples ⊆ SERVICES × RELATIONS × (SERVICES ∪ RESOURCES)`, `compromised ⊆ SERVICES`
- **Actions:** AddTuple, RemoveTuple, CompromiseService, AttackerAddTuple
- **State space size** (for testbed configuration: 4 services, 4 resources, 3 relations): 2^(4×3×8) × 2^4 = 2^112 states (TLC uses symbolic BFS, not enumeration)
- **Verification time:** 12 minutes on a 4-core MacBook Pro for the testbed configuration

The state space is finite because: (a) SERVICES, RESOURCES, and RELATIONS are finite constants; (b) tuples is bounded by |SERVICES| × |RELATIONS| × |SERVICES ∪ RESOURCES|.

### 3.5.3 Invariants

**NoPrivilegeEscalation:**
```tla
NoPrivilegeEscalation ==
  \A s \in SERVICES :
    \A o \in ReachableFrom(s) :
      PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]
```

This invariant states that for every service `s`, every object reachable from `s` via any sequence of can_call/can_read/can_write relations must have a permission level ≤ the permission level of `s`. "Reachable" is defined as direct (one-hop) in the current model; the specification notes that multi-hop transitive reachability requires a recursive fixpoint operator (see Limitations, Chapter 5).

**NoLateralMovement:**
```tla
NoLateralMovement ==
  \A a \in compromised :
    \A <<s, r, o>> \in tuples :
      s = a => PERMISSION_LEVEL[a] >= PERMISSION_LEVEL[o]
```

This invariant states that every tuple whose subject is a compromised service must point to an object at or below the compromised service's permission level. Combined with the fact that AttackerAddTuple can only add tuples with the attacker as subject, this ensures a compromised service cannot grant itself access to higher-privilege resources.

**The key TLC finding (Month 6 research log):**

TLC found a counterexample for NoPrivilegeEscalation in the initial test policy. The counterexample trace was:
1. AddTuple(svc_frontend, can_call, svc_logger) — intended
2. AddTuple(svc_logger, can_read, db_sensitive) — intended
3. AttackerAddTuple(svc_logger, can_call, svc_frontend) — attacker compromises svc_logger

State after step 3: svc_frontend can call svc_logger (step 1), and svc_logger can now call svc_frontend (step 3 — attacker-added). This creates a cycle, but more importantly: step 2 means svc_logger has read access to db_sensitive. With svc_logger compromised and calling svc_frontend, the attacker can exfiltrate data through svc_logger → db_sensitive.

PERMISSION_LEVEL[svc_frontend] = 1 (low-trust, user-facing).
PERMISSION_LEVEL[db_sensitive] = 3 (high-trust, data layer).
Violation: a PERMISSION_LEVEL=1 service chain reaches PERMISSION_LEVEL=3 resource.

**Fix:** Remove the tuple `(svc_logger, can_read, db_sensitive)`. Logger services should write to a log aggregator (PERMISSION_LEVEL=1), not read from a database.

### 3.5.4 FV-Zanzibar Workflow

The formal verification process is integrated into the authorization policy deployment workflow:

```
Policy author writes Keto tuples
        ↓
FV-Zanzibar: translate tuples to TLA+ constants
        ↓
TLC model checker runs (~ 12 minutes)
        ↓ 
  Verified? ──YES──→ Deploy policy to Keto
        │
       NO
        ↓
  Counterexample printed (specific tuple sequence that violates invariant)
        ↓
  Policy author fixes the violating tuple
        ↓
  Repeat
```

The translation from Keto tuples to TLA+ constants is mechanical: each tuple `(s, r, o)` maps to a TLA+ triple in the SERVICES, RELATIONS, RESOURCES sets; PERMISSION_LEVEL is a manually assigned mapping based on the service's role in the architecture.

Full specification: [03_prototype/tla_specs/Authorization.tla](../03_prototype/tla_specs/Authorization.tla)

---

## 3.6 Evaluation Design

### 3.6.1 Testbed Configuration

**Hardware:** MacBook Pro (Apple M2, 16 GB RAM). Kubernetes via minikube v1.31 with Docker driver.

**Service topology:**
```
svc_frontend (NodePort:30080) → svc_api (NodePort:30090) → svc_db (ClusterIP)
                                      ↕
                              svc_cache (ClusterIP)
```

**Keto version:** v0.11.1 (https://github.com/ory/keto/releases)
**Keto backend:** In-memory (for development) and PostgreSQL 15 (for persistence evaluation)

### 3.6.2 Evaluation Metrics (Summary)

| Metric | Definition | Target |
|--------|-----------|--------|
| MTTC | Mean time from attack start to successful exploitation | Maximize (vs. baseline) |
| Attack Surface Shift | % of endpoints changed per rotation | ~100% per 60s |
| SDR | % of legitimate requests failing due to MTD | < 1% |
| Entropy alert latency | Time from DDoS start to first alert | < 30s |
| CUSUM alert latency | Time from lateral movement start to first alert | < 60s |
| F1 score | Harmonic mean of precision and recall on CIC-IDS2017 | > 90% |
| FPR | False positive rate | < 2% |
| TLC verification time | Wall-clock time for TLC on testbed policy | < 30 minutes |
| Policy bug detection | Proportion of misconfigured policies where TLC finds a violation | > 30% |

### 3.6.3 MTD Evaluation Protocol

**Experiment 1 — Baseline (no MTD):**
Attacker runs nmap against the cluster (`nmap -p 30000-32767 <node-ip>`). Time from nmap start to first successful connection is recorded as MTTC_baseline.

**Experiment 2 — MTD active (T = 60s):**
Same attacker with same nmap. After each MKE rotation, the attacker must re-scan. MTTC_mtd is recorded.

**Experiment 3 — Slow port scan (attacker rate-limits to 1 probe/5s):**
Tests whether a patient attacker can evade MTD by scanning slowly. Expected result: rotation completes before scan completes.

Both experiments are repeated 30 times; results are reported as mean ± standard deviation.

### 3.6.4 Statistical Detector Evaluation Protocol

**CIC-IDS2017 evaluation:**
The DDoS and DoS subsets of CIC-IDS2017 (https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html) are loaded. NetFlow features are adapted to the Keto log format (source IP → source service name, destination IP → target service name, packet count → request count per window). The detector runs offline on the dataset.

Labels are binary: attack / normal. The detector outputs an alert per window per service-pair; a window is labelled "detected" if any alert is raised for the correct service-pair within 60 seconds of the attack start.

Three detector configurations are evaluated: Entropy only, CUSUM only, Entropy + CUSUM (combined).

**Testbed evaluation (live):**
The detector runs live in minikube. A synthetic DDoS is generated by flooding svc_api with HTTP requests from a test pod. A synthetic lateral movement is simulated by configuring svc_frontend to call svc_db at 10× its normal rate.

### 3.6.5 TLA+ Evaluation Protocol

Five authorization policy configurations are tested:
1. **Clean policy** (no bugs): minimal tuples matching the threat model
2. **Transitive logging bug** (the bug found in Month 6): svc_logger has read access to db_sensitive
3. **Wildcard over-grant**: svc_api has `can_call` to `*` (all services)
4. **Circular trust**: svc_frontend and svc_api each grant the other elevated access
5. **Admin creep**: svc_monitoring has accumulated can_read to 8/10 resources over time

Expected: TLC finds violations in policies 2–5; policy 1 passes. Bug detection rate = 4/5 = 80% (the reported result in Chapter 4 is 2/5 = 40%, which was the first run before adding the wildcard and circular trust scenarios).

---

## References

- Blazek, R.B. et al. (2001). CUSUM for DoS detection. *IEEE IWIAS.* DOI: https://doi.org/10.1109/IWIAS.2001.935077
- Chandola, V. et al. (2009). Anomaly detection: A survey. *ACM Computing Surveys.* DOI: https://doi.org/10.1145/1541880.1541882
- Dolev, D. & Yao, A. (1983). On the security of public key protocols. *IEEE TIT, 29*(2), 198-208.
- Jajodia, S. et al. (eds.) (2011). *Moving Target Defense.* Springer. DOI: https://doi.org/10.1007/978-1-4614-0977-9
- Lamport, L. (2002). *Specifying Systems.* Free: https://lamport.azurewebsites.net/tla/book.html
- Newcombe, C. et al. (2015). How AWS uses formal methods. *CACM, 58*(4). DOI: https://doi.org/10.1145/2699417
- Nychis, G. et al. (2008). Entropy-based traffic anomaly detection. *ACM IMC.* DOI: https://doi.org/10.1145/1452520.1452539
- Ory Keto: https://github.com/ory/keto
- Pang, R. et al. (2019). Zanzibar. *USENIX ATC.* https://www.usenix.org/conference/atc19/presentation/pang
- Rose, S. et al. (2020). Zero Trust Architecture. *NIST SP 800-207.* https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf
- Sengupta, S. et al. (2020). MTD survey. *IEEE COMST, 22*(3). DOI: https://doi.org/10.1109/COMST.2020.2982955
