# PhD Research Repository
## Moving Target Defense & Formal Authorization Verification
## for Securing Distributed Microservices Against Network Attacks

**Candidate:** Deidine Cheigeur
**Degree:** PhD in Computer Science
**Field:** Cybersecurity + Distributed Systems
**Status:** Year 2 — Thesis writing + Evaluation
**Target defence:** December 2026

---

## Research Summary

This thesis proposes a three-layer security framework for distributed microservices that uses **no machine learning**. It addresses three open problems in cloud-native security:

| Problem | Solution | Key result |
|---------|----------|------------|
| Static endpoints enable rapid attacker reconnaissance | MTD Engine for Kubernetes (MKE): rotates NodePort every 60s | MTTC **7.6×** better than baseline |
| Authorization policies have undetected logical flaws | FV-Zanzibar: TLA+ formal verification before deployment | **4/5** buggy policies detected |
| ML detectors need training data + produce opaque alerts | SAAD: Shannon entropy + CUSUM on Keto audit logs | F1 = **94.0%**, FPR = **1.1%** |

**Authorization platform:** Ory Keto — open-source Google Zanzibar implementation
GitHub: https://github.com/ory/keto

**No ML used anywhere in this thesis.** All detection is statistical; all verification is formal.

---

## Repository Structure

```
phd/
│
├── README.md                           ← YOU ARE HERE
│
├── 01_paper_summaries/                 ← All 15 papers read + summarized (DOI links in every file)
│   ├── index.md                        ← Master index by theme
│   ├── P01_Anderson_Security_Engineering.md
│   ├── P02_Zanzibar_Pang_2019.md       ← ★ Core paper — motivates C3
│   ├── P03_Newcombe_AWS_TLA_2015.md    ← ★ TLA+ justification (AWS found real bugs)
│   ├── P04_Sengupta_MTD_Survey_2020.md ← ★ Explicit gap: "MTD for Kubernetes unsolved"
│   ├── P05_Lamport_TLA_2002.md
│   ├── P06_Sandhu_AccessControl_1994.md
│   ├── P07_Chandola_Anomaly_Detection_2009.md
│   ├── P08_CUSUM_Blazek_2001.md
│   ├── P09_Entropy_Nychis_2008.md
│   ├── P10_MTD_Microservices_MDPI_2024.md
│   ├── P11_Tanenbaum_DistributedSystems.md
│   ├── P12_Hoque_Attack_Taxonomy.md
│   ├── P13_NIST_ZeroTrust.md
│   ├── P14_Jajodia_MTD_Book.md
│   └── P15_Ryan_FormalMethods_Security.md ← ★ Gap: "no TLA+ for Zanzibar" confirmed
│
├── 02_thesis/                          ← Thesis chapters
│   ├── thesis_outline.md               ← Abstract + table of contents + word counts
│   ├── chapter1_introduction.md        ← COMPLETE (~3,500 words)
│   ├── chapter2_background.md          ← COMPLETE (~8,200 words)
│   └── chapter3_methodology.md         ← COMPLETE (~5,800 words)
│
├── 03_prototype/                       ← Working prototype code
│   ├── mtd_controller/
│   │   ├── mtd_controller.py           ← Layer 1: MKE Kubernetes MTD controller
│   │   └── requirements.txt
│   ├── statistical_detector/
│   │   ├── detector.py                 ← Layer 2: SAAD — entropy + CUSUM
│   │   └── requirements.txt
│   └── tla_specs/
│       └── Authorization.tla           ← Layer 3: FV-Zanzibar TLA+ spec
│
├── 04_conference_paper/                ← IEEE CloudCom 2026 submission
│   ├── paper_draft.md                  ← 8-page paper (complete draft)
│   └── references.bib                  ← BibTeX (15 entries)
│
├── 05_research_log/
│   └── two_year_log.md                 ← 22-month research log with experimental results
│
└── reserch/                            ← Early-stage notes (kept for history)
    ├── thesis_topic.md
    ├── PhD_2Year_Catchup_Plan.md
    ├── literature_review.md
    └── research_summary.md
```

---

## How the Pieces Connect

```
PAPERS (01/)              THESIS (02/)               PROTOTYPE (03/)
│                          │                          │
P04 Sengupta 2020         Ch.2 §2.3                  mtd_controller.py
"MTD/k8s: open" ─────────►"MTD background" ──────────►"MKE implementation"
                           │                          │
P02 Zanzibar 2019         Ch.2 §2.2.4                Authorization.tla
"No formal verif." ───────►"ReBAC + Zanzibar" ────────►"FV-Zanzibar spec"
                           │                          │
P07+P08+P09               Ch.2 §2.5                  detector.py
Chandola+Blazek+Nychis ───►"Statistical methods" ─────►"SAAD detector"
                           │
                          Ch.3 §3.6 (evaluation design)
                           │
                          CONFERENCE PAPER (04/)
                          paper_draft.md ◄── Tables 1–3 (Ch.4 results)
                          references.bib

RESEARCH LOG (05/)
two_year_log.md ◄────── records all decisions, experiments, bugs found
```

---

## Three Contributions

### C1 — MTD Engine for Kubernetes (MKE)

**Code:** [03_prototype/mtd_controller/mtd_controller.py](03_prototype/mtd_controller/mtd_controller.py)

Rotates Kubernetes NodePort endpoints every 60 seconds. Atomically updates Ory Keto authorization tuples so only authorized clients discover the new port. Clients query Keto before each request — no cached endpoints.

```
Rotation algorithm:
  1. new_port ← random ∈ [30000, 32767]
  2. Update Keto tuple with new_port   ← FIRST (atomic)
  3. Patch Kubernetes NodePort         ← SECOND
  4. schedule(rotate, delay=60s)
```

**Result:** MTTC (mean time to compromise) 7.6× better with MKE vs. baseline.

**Key gap reference:** Sengupta et al. (2020) §VI.D: "Application of MTD to cloud-native container-orchestrated environments remains an open research direction."
DOI: https://doi.org/10.1109/COMST.2020.2982955

---

### C2 — Statistical Authorization Anomaly Detector (SAAD)

**Code:** [03_prototype/statistical_detector/detector.py](03_prototype/statistical_detector/detector.py)

Reads Ory Keto authorization request audit log. Computes per-service Shannon entropy and per-pair CUSUM every 10 seconds.

```
Shannon entropy: H(X) = -Σ p(x) log₂ p(x)
Alert if H drops 40%+ below baseline  → DDoS suspected

CUSUM: S(t) = max(0, S(t-1) + (x - μ₀ - k))
Alert if S(t) > 5σ                    → Lateral movement / slow attack
```

**Result:** F1 = 94.0%, FPR = 1.1% on CIC-IDS2017. Zero training data required.

Dataset: https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html

---

### C3 — FV-Zanzibar: TLA+ Formal Verification

**Spec:** [03_prototype/tla_specs/Authorization.tla](03_prototype/tla_specs/Authorization.tla)

Models Ory Keto authorization as a TLA+ state machine including adversarial actions. TLC verifies two safety invariants against all reachable states:

```tla
NoPrivilegeEscalation:
  ∀ service s, ∀ object o reachable from s:
    PERMISSION_LEVEL[s] ≥ PERMISSION_LEVEL[o]

NoLateralMovement:
  ∀ compromised service a, ∀ tuple ⟨a, r, o⟩:
    PERMISSION_LEVEL[a] ≥ PERMISSION_LEVEL[o]
```

**Key finding:** TLC found a transitive privilege escalation via svc_logger → db_sensitive that escaped code review. Counterexample: frontend (level=1) reaches sensitive DB (level=3) through a shared logger.

**Run:**
```bash
# VS Code extension: https://marketplace.visualstudio.com/items?itemName=alygin.vscode-tlaplus
java -jar tla2tools.jar -config Authorization.cfg Authorization.tla
```

**Result:** 4/5 buggy policy configurations detected.

**Key gap reference:** Ryan et al. (2023): "no published work applies TLA+ to authorization policy correctness in production authorization systems."
DOI: https://doi.org/10.1145/3522582

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/[username]/phd-mtd-zanzibar-security

# Layer 1 — MTD Controller
cd 03_prototype/mtd_controller
pip install -r requirements.txt
python mtd_controller.py

# Layer 2 — Statistical Detector
cd 03_prototype/statistical_detector
pip install -r requirements.txt
python detector.py

# Layer 3 — TLA+ Verification
# Install toolbox: https://lamport.azurewebsites.net/tla/toolbox.html
cd 03_prototype/tla_specs
java -jar /path/to/tla2tools.jar Authorization.tla
```

**Prerequisites:** minikube, Ory Keto
- minikube: https://minikube.sigs.k8s.io/docs/start/
- Keto install: `helm install keto ory/keto --set keto.config.dsn=memory`
  Docs: https://www.ory.sh/docs/keto/install

---

## Experimental Results Summary

### MTD Effectiveness (Table 1)

| Scenario | MTTC no MTD | MTTC with MKE | Improvement |
|----------|-------------|---------------|-------------|
| Port scan (nmap) | 28s | 214s | **7.6×** |
| Service enumeration | 45s | 318s | **7.1×** |
| Exploit attempt | 62s | 471s | **7.6×** |

Service Disruption Rate at T=60s: **0.8%** (target: < 1%)

### Statistical Detector (Table 2, CIC-IDS2017)

| Method | F1 | FPR |
|--------|----|-----|
| Entropy only | 89.2% | 1.8% |
| CUSUM only | 85.1% | 2.4% |
| **Entropy + CUSUM** | **94.0%** | **1.1%** |

### TLA+ Verification (Table 3)

| Policy | Bug | TLC result |
|--------|-----|-----------|
| Clean baseline | None | Pass (8m 42s) |
| Transitive logging | NoPrivilegeEscalation | **FOUND** (11m 17s) |
| Wildcard over-grant | Both invariants | **FOUND** (12m 04s) |
| Circular trust | NoLateralMovement | **FOUND** (9m 51s) |
| Admin creep | NoPrivilegeEscalation | **FOUND** (13m 22s) |

---

## Publication Targets

| Venue | Status | Deadline | Link |
|-------|--------|----------|------|
| IEEE CloudCom 2026 | Draft ready | August 2026 | https://www.cloudcomputing-conference.net/ |
| IEEE TDSC (journal) | Planned | Month 19 | https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8858 |

---

## Technology Stack

| Tool | Purpose | Link |
|------|---------|------|
| Kubernetes (minikube) | Microservices orchestration | https://minikube.sigs.k8s.io/ |
| Ory Keto | ReBAC authorization (Zanzibar-based) | https://github.com/ory/keto |
| TLA+ / TLC | Formal specification + model checking | https://lamport.azurewebsites.net/tla/ |
| Python 3.11 | MTD controller + statistical detector | https://python.org |
| CIC-IDS2017 | Evaluation dataset | https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html |
