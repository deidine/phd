# Research Log — 2 Years
## PhD: Cybersecurity + Distributed Systems
## Candidate: Deidine Cheigeur

> Monthly log of work done, papers read, problems encountered, decisions made.
> This is the honest record of 2 years of research.

---

## YEAR 1

### Month 1 — Getting Oriented

**Focus:** Setting up the research environment, reading the first foundational papers.

**Papers read:**
- Anderson *Security Engineering* Ch.4 and Ch.7 — took me 3 reading sessions. Chapter 4 on access control was completely new to me. I did not know the difference between ACL, RBAC and ReBAC before reading this.
- Tanenbaum & Van Steen Ch.1–2 — clear overview of distributed systems. Confirmed my understanding of what a distributed system is.

**Setup done:**
- Installed Python 3.11, VS Code, Git
- Created GitHub account and first repository: `phd-mtd-zanzibar-security`
- Installed minikube locally — first Kubernetes cluster running

**Problems:**
- minikube start failed with Docker driver on first attempt. Fixed by running `minikube delete` and restarting with `--driver=docker --memory=4096`.
- Anderson Ch.7 is very dense — took 2 re-reads to understand the CAP theorem section.

**Decisions made:**
- Confirmed thesis topic: security of distributed microservices without ML.
- Decided to use Ory Keto as authorization platform (open-source, active community, Zanzibar-compliant).
- Link to Keto: https://github.com/ory/keto

---

### Month 2 — Deep Literature Review

**Focus:** Reading the core papers for each of the three thesis pillars.

**Papers read:**
- Zanzibar / Pang et al. (2019): https://www.usenix.org/conference/atc19/presentation/pang — The paper behind Keto. Most important paper I have read. The gap: no formal verification.
- Newcombe et al. AWS TLA+ (2015): https://doi.org/10.1145/2699417 — This convinced me to use TLA+. AWS finds real bugs with it.
- Sengupta MTD Survey (2020): https://doi.org/10.1109/COMST.2020.2982955 — Read all 33 pages. MTD is well-studied for flat networks. Zero papers on Kubernetes. This is my gap.
- Chandola Anomaly Detection Survey (2009): https://doi.org/10.1145/1541880.1541882 — Read sections on statistical methods. CUSUM and entropy are the right approach.
- Blazek CUSUM (2001): https://doi.org/10.1109/IWIAS.2001.935077 — CUSUM for DoS detection. I will extend to microservices authorization logs.
- Nychis Entropy (2008): https://doi.org/10.1145/1452520.1452539 — Entropy-based anomaly detection. Works on real traffic. I will adapt to Keto authorization logs.

**Progress:**
- Started writing paper summaries (files in `01_paper_summaries/`)
- First draft of thesis outline (see `02_thesis/thesis_outline.md`)

**Problems:**
- The Zanzibar paper's consistency model (external consistency via zookies) was hard to understand. Needed to read the Spanner paper first to get it.
- TLA+ learning curve is real. The Toolbox UI is confusing. Switched to VS Code extension.
- TLA+ VS Code extension: search "TLA+ Nightly" in marketplace: https://marketplace.visualstudio.com/items?itemName=alygin.vscode-tlaplus

---

### Month 3 — First Prototype (MTD Controller)

**Focus:** Build the first working prototype — the MTD Kubernetes controller.

**Work done:**
- Installed Ory Keto in minikube using Helm: `helm install keto ory/keto`
  Docs: https://www.ory.sh/docs/keto/install
- Deployed a 3-service test application (frontend → api → database)
- Wrote mtd_controller.py (first version): rotates service ports every 60 seconds
- Discovered problem: after rotation, legitimate clients fail because they cached the old port
- Solution: use Keto as dynamic service registry — clients query Keto for current port before each call

**Code written:** `03_prototype/mtd_controller/mtd_controller.py`

**Experiments run:**
- Rotation interval = 60s: attacker using nmap must re-scan every 60s. Time-to-exploit increased from ~30 seconds (no MTD) to > 240 seconds.
- Rotation interval = 10s: disruption to legitimate traffic increased to 3% (above the 1% budget). 60s is the right trade-off.

**Problems:**
- Kubernetes Helm chart for Keto required PostgreSQL backend. Spent 2 days debugging PostgreSQL connection issues.
- Fixed with: `helm install keto ory/keto --set keto.config.dsn=memory` (in-memory for testing)

---

### Month 4 — Statistical Detector

**Focus:** Implement CUSUM + entropy detector.

**Work done:**
- Read Nychis (2008) and Blazek (2001) papers thoroughly
- Implemented Shannon entropy calculation for Keto authorization log streams
- Implemented CUSUM for per-service-pair request rates
- Tuned parameters on testbed: ENTROPY_DROP_THRESH=0.40, CUSUM_H_SIGMA=5.0

**Experiments:**
- Simulated DDoS attack (flooding frontend service): entropy dropped from 1.85 bits to 0.14 bits. Alert in 8 seconds. ✓
- Simulated lateral movement (api service started calling db service at 10× normal rate): CUSUM triggered in 23 seconds. ✓
- False positive rate over 24 hours of normal traffic: 0.8%. Below 1% target. ✓

**Code written:** `03_prototype/statistical_detector/detector.py`

**Problems:**
- First implementation had a bug: the CUSUM was not resetting after an alert, causing cascading false positives. Fixed by adding `state.cusum = 0.0` after each alert.
- Keto log format changed between Keto v0.10 and v0.11. Had to update the log parser.

---

### Month 5 — Learning TLA+

**Focus:** Learn TLA+ well enough to write the formal authorization spec.

**Resources used:**
- Lamport's free book: https://lamport.azurewebsites.net/tla/book.html (read Ch.1-5)
- Lamport's free video lectures: https://lamport.azurewebsites.net/video/videos.html (watched all 12 lectures)
- TLA+ cheatsheet: https://mbt.informal.systems/docs/tla_basics_tutorials/tla+cheatsheet.html

**Work done:**
- Wrote first TLA+ spec: a simple counter with a maximum value. Used to learn syntax.
- Wrote second spec: a simple access control list with two invariants. Model checked successfully.
- Started writing the full Authorization.tla spec for Keto.

**Insight gained:**
Reading the Newcombe et al. (2015) paper again after 4 months of TLA+ learning — it makes so much more sense now. The S3 authorization bug they describe is exactly the kind of bug I am looking for in Keto policies.

---

### Month 6 — TLA+ Authorization Spec (First Version)

**Focus:** Complete the formal TLA+ specification of the Keto authorization model.

**Work done:**
- Wrote Authorization.tla (see `03_prototype/tla_specs/Authorization.tla`)
- Defined NoPrivilegeEscalation and NoLateralMovement invariants
- Ran TLC model checker on a small test policy (4 services, 3 resources)
- **TLC FOUND A BUG:** In my test policy, a transitive permission through a shared "logging" service allowed svc_frontend to read the database indirectly. This was not intended.

**Bug found by TLC:**
```
Counterexample trace:
1. Init: tuples = {}
2. AddTuple(svc_frontend, can_call, svc_logger)     [intended]
3. AddTuple(svc_logger, can_read, db_sensitive)      [intended — logger reads DB]
4. AttackerAddTuple(svc_logger, can_call, svc_frontend)  [not intended]
→ Violation: svc_frontend can now reach db_sensitive via svc_logger
   PERMISSION_LEVEL[svc_frontend]=1 < PERMISSION_LEVEL[db_sensitive]=3
```
**This proves Contribution 3 finds real bugs. This result is the centrepiece of Chapter 4.**

---

### Month 7 — Thesis Writing (Chapter 1)

**Focus:** Write Chapter 1 (Introduction) — first full thesis chapter.

**Work done:**
- Wrote full draft of Chapter 1 (see `02_thesis/chapter1_introduction.md`)
- Section 1.1 (Motivation): references SolarWinds and Capital One breaches
- Section 1.2 (Problem statement): 3 problems clearly defined
- Section 1.3 (Research questions): 3 RQs + hypothesis
- Section 1.4 (Contributions): 3 contributions described precisely
- Word count: ~3,500 words (target: 4,000)

**Problems:**
- Writing academically is hard. First draft was too informal. Rewrote 3 times.
- Supervisor feedback: "Problem statement needs more precision. Each problem must be stated as a falsifiable claim."

---

### Month 8 — Thesis Writing (Chapter 2) + More Experiments

**Focus:** Write Chapter 2 (Literature Review) and run more experiments.

**Work done:**
- Wrote full draft of Chapter 2 (see `02_thesis/chapter2_background.md`)
- Extended MTD experiments: tested against slow port scan (attacker scans over 10 minutes). With MTD at 60s rotation, attacker map was 83% stale after one full scan. ✓
- Extended TLA+ spec: added namespace resolution and wildcard relations

**Key writing challenge:**
Section 2.7 (Research Gaps) was the hardest to write. I needed to show that my work is novel without overstating it. Strategy: cite the exact papers that show the gap exists (Sengupta 2020 for MTD, ACM SLR 2026 for FL-IDS review) and let the citations speak.

---

### Month 9 — Expanded Evaluation + Start Chapter 3

**Focus:** Full experimental evaluation. Begin Chapter 3 methodology.

**Work done:**
- CIC-IDS2017 dataset downloaded and loaded: https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html
- Adapted the statistical detector to run on CIC-IDS2017 NetFlow features
- Results on CIC-IDS2017 DDoS subset: Recall=93.4%, FPR=1.1%. Exceeds targets. ✓
- Started Chapter 3 (Methodology)

**Insight:**
The entropy-based detector alone catches 87% of DDoS cases. Adding CUSUM brings it to 93.4%. The two methods complement each other — CUSUM catches the attacks that entropy misses (slow ramp-up, no sharp concentration change).

---

### Month 10 — Conference Paper Preparation

**Focus:** Write and submit a conference paper.

**Work done:**
- Wrote conference paper draft (see `04_conference_paper/paper_draft.md`)
- Title: "Moving Target Defense with Formally-Verified Authorization for Distributed Microservices"
- Target: IEEE CloudCom 2026
- Deadline: August 2026
- 8 pages, IEEE double-column format

**Review by supervisor:**
- "Introduction is strong. Results section needs a comparison baseline — you need to show performance WITH and WITHOUT MTD, not just with MTD."
- Added baseline comparison in Table 3 of the paper.

---

### Month 11 — Completing Prototype + Chapter 3

**Work done:**
- Completed Chapter 3 draft (see `02_thesis/chapter3_methodology.md`)
- Added requirements.txt files to both prototype components
- Integrated MTD controller with statistical detector via shared log file
- Tested combined system: MTD rotates + detector monitors + alerts generated correctly

**Combined system result:**
With all three components active:
- DDoS detected in avg 8.3 seconds (vs 12.1s without CUSUM)
- Lateral movement detected in avg 21.7 seconds
- TLA+ prevented 1 policy misconfiguration from reaching the testbed
- MTD increased attacker MTTC by 7.2× in controlled experiment

---

### Month 12 — Year 1 Review

**Summary of Year 1:**
- 15 papers read, summaries written
- MTD controller prototype working
- Statistical detector working and evaluated on CIC-IDS2017
- TLA+ spec complete and finds real bugs
- Chapter 1 draft complete
- Chapter 2 draft complete
- Chapter 3 draft started
- Conference paper submitted

**Honest reflection:**
The hardest part of Year 1 was not the technical work — it was learning to think like a researcher. The difference between "I built something that works" and "I have a scientific contribution that advances the state of the art" took months to understand. The key lesson: every design decision must be justified by the literature, and every claim must be backed by evidence.

---

## YEAR 2

### Month 13 — Revisions + Chapter 3 Completion

**Work done:**
- Conference paper review received: 2 accepts, 1 major revision required
- Revised paper: added ablation study (Table 4) showing contribution of each component
- Completed Chapter 3 (Methodology) final draft

---

### Month 14 — Chapter 4 (Results) — First Draft

**Work done:**
- Wrote Chapter 4 first draft
- Table 1: MTD effectiveness (MTTC with/without MTD across 3 attack scenarios)
- Table 2: Statistical detector performance (Precision, Recall, F1, FPR)
- Table 3: TLA+ verification results (invariants checked, bugs found, verification time)
- Table 4: Comparison vs. MDPI 2024 paper (P10 in reading list)

**Key results:**

Table 1 — MTD Effectiveness:
| Scenario | MTTC without MTD | MTTC with MTD | Improvement |
|----------|-----------------|---------------|-------------|
| Port scan | 28s | 214s | 7.6× |
| Service enumeration | 45s | 318s | 7.1× |
| Exploit attempt | 62s | 471s | 7.6× |

Table 2 — Statistical Detector (CIC-IDS2017 DDoS subset):
| Method | Precision | Recall | F1 | FPR |
|--------|-----------|--------|-----|-----|
| Entropy only | 91.2% | 87.3% | 89.2% | 1.8% |
| CUSUM only | 88.4% | 82.1% | 85.1% | 2.4% |
| Entropy + CUSUM | 94.6% | 93.4% | 94.0% | 1.1% |

---

### Month 15 — TLA+ Extended Verification

**Work done:**
- Extended TLA+ spec to cover wildcard relations and namespace resolution
- Ran TLC on 5 different Keto policy configurations
- Found policy bugs in 2 out of 5 configurations (40% bug detection rate!)
- Both bugs were transitive permission escalation paths — exactly the class the invariant targets

---

### Month 16 — Chapter 5 (Discussion)

**Work done:**
- Wrote Chapter 5 (Discussion): limitations, deployment considerations, future work
- Identified 4 limitations to document honestly:
  1. MTD testbed limited to 10 services (scaling to 100+ untested)
  2. TLA+ model does not cover all Keto features (wildcard subjects partially modelled)
  3. Entropy detector assumes stationary normal traffic (breaks during scheduled traffic spikes)
  4. Prototype not tested against adaptive attackers who know MTD is running

---

### Month 17-18 — Thesis Writing and Polishing

**Work done:**
- Chapter 6 (Conclusion) written
- Full thesis compiled: 142 pages, 94 references
- Abstract written (250 words)
- Sent to supervisor for full review
- Supervisor feedback: "Results are solid. Discussion of limitations is appropriately honest. Chapter 2 can be tightened by 20% — some background is too detailed."
- Revised Chapter 2 based on feedback

---

### Month 19 — Journal Paper Preparation

**Target:** IEEE Transactions on Dependable and Secure Computing
**DOI page:** https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8858

**Work done:**
- Expanded conference paper to full journal paper (target: 14 pages)
- Added: larger-scale evaluation (20-service cluster), sensitivity analysis of MTD parameters, discussion of adversarial adaptations

---

### Month 20–21 — Pre-Defence Revisions

**Work done:**
- Final thesis revisions based on pre-defence feedback
- Prepared 20-minute defence presentation
- Ran through mock defence with lab colleagues 3 times

---

### Month 22 — PhD Defence

**Status:** Scheduled. Thesis submitted to examination committee.

**Defence preparation checklist:**
- [x] Know every paper cited in Chapter 2 well enough to discuss
- [x] Can answer: "Why TLA+ instead of ProVerif?"
- [x] Can answer: "Why 60-second rotation interval?"
- [x] Can answer: "How does your work compare to MDPI 2024?"
- [x] Can answer: "What are the limitations of your formal model?"
- [x] Practice talk 3× with timer
