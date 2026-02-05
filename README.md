# PhD Research — Federated Intrusion Detection for Cloud-Native Microservices

> **Candidate:** Deidine Cheigeur
> **Field:** Cybersecurity + Distributed Systems
> **Thesis title:** Federated Multi-Layer Intrusion Detection and Automated Response for Distributed Cyber Attacks in Cloud-Native Microservices Architectures
> **Supervisor:** [Assigned]
> **Started:** June 2026

---

## Quick Links

| Document | What it is |
|----------|-----------|
| [reserch/thesis_topic.md](reserch/thesis_topic.md) | Assigned thesis title, research question, 3 contributions, novelty |
| [reserch/PhD_2Year_Catchup_Plan.md](reserch/PhD_2Year_Catchup_Plan.md) | 6-month sprint plan with 25 papers + weekly schedule |
| [reserch/literature_review.md](reserch/literature_review.md) | Full literature review — 18 papers, 5 themes |
| [reserch/research_summary.md](reserch/research_summary.md) | Book + 3 key articles summaries |
| [PhD_Thesis_Proposal_FederatedIDS_Microservices.pptx](PhD_Thesis_Proposal_FederatedIDS_Microservices.pptx) | 8-slide presentation |

---

## Thesis in One Paragraph

Modern cloud applications use **microservices** — dozens of small services running
in Docker containers, orchestrated by Kubernetes, communicating via REST/gRPC.
This creates a distributed attack surface vulnerable to DDoS, lateral movement,
MITM, and API abuse. Existing intrusion detection systems (IDS) were designed for
flat enterprise networks and cannot handle the ephemeral, multi-tenant nature of
cloud-native environments. This thesis proposes a **federated intrusion detection
framework** that extracts features from **Istio service-mesh telemetry**, trains a
shared detection model across multiple clusters using **FedAvg** (without sharing
raw traffic data), and automatically generates **Kubernetes NetworkPolicies** to
isolate attacked services in real time. The system is evaluated on CIC-IDS2017,
UNSW-NB15, and a live Kubernetes testbed.

---

## The Three Contributions

| # | Contribution | Novelty |
|---|-------------|---------|
| C1 | Service-mesh feature extractor (Istio/Envoy telemetry) | No IDS paper uses service-mesh call-graph features |
| C2 | Federated LSTM-Autoencoder across Kubernetes clusters | No FL-IDS paper targets Kubernetes microservices (ACM SLR 2026) |
| C3 | Automated NetworkPolicy response (<1s) | No FL-IDS paper closes the detection-to-response loop |

---

## Repository Structure

```
phd/
├── README.md
├── PhD_Thesis_Proposal_FederatedIDS_Microservices.pptx
├── generate_presentation.py
├── semaine1.md                    ← Week 1: Python foundations
│
├── reserch/
│   ├── thesis_topic.md            ← Assigned topic + novelty
│   ├── PhD_2Year_Catchup_Plan.md  ← 6-month sprint plan
│   ├── literature_review.md       ← 18 papers, 5 themes
│   └── research_summary.md        ← Book + 3 key articles
│
└── pyhton/                        ← Python exercises
```

---

## Mini Project (To Build)

**GitHub repo name:** `phd-federated-ids-microservices`

```
phd-federated-ids-microservices/
├── feature_extractor/    ← Istio telemetry → feature vectors
├── fl_server/            ← FedAvg aggregation (Flower)
├── fl_client/            ← LSTM-Autoencoder per cluster
├── response/             ← Kubernetes NetworkPolicy generator
├── evaluation/           ← CIC-IDS2017 + UNSW-NB15 pipeline
└── tests/
```

---

## 25-Paper Reading List (Priority Order)

See [reserch/PhD_2Year_Catchup_Plan.md](reserch/PhD_2Year_Catchup_Plan.md) for the full list with free PDF links.

Top 5 to read first:
1. Khraisat et al. (2019) — IDS survey — https://cybersecurity.springeropen.com/articles/10.1186/s42400-019-0038-7
2. ACM SLR (2026) — FL-IDS gaps — https://dl.acm.org/doi/10.1145/3731596
3. McMahan et al. (2017) — FedAvg — https://arxiv.org/abs/1602.05629
4. Sharafaldin et al. (2018) — CIC-IDS2017 dataset
5. Zhao et al. (2018) — Non-IID FL — https://arxiv.org/abs/1806.00582

---

## Install Tools (Do This First)

```bash
pip install scikit-learn pandas numpy matplotlib seaborn shap flwr torch

brew install minikube
minikube start --driver=docker

curl -L https://istio.io/downloadIstio | sh -
istioctl install --set profile=demo

# Paper manager
# Download Zotero: https://www.zotero.org/
```

---

## Weekly Progress Log

| Week | Focus | Status |
|------|-------|--------|
| 1 | Python foundations | ✓ Done (semaine1.md) |
| 2 | Read Papers 1–7, write summaries | |
| 3 | Read Papers 8–15, write summaries | |
| 4 | Read Papers 16–25, write summaries | |
| 5–6 | Write Thesis Chapter 1 (Introduction) | |
| 7–8 | Write Thesis Chapter 2 (Literature Review) | |
| 9–12 | Build mini project prototype | |
| 13–16 | Write Thesis Chapter 3 (Methodology) | |
| 17–20 | Write Thesis Chapter 4 (Results) + submit conference paper | |
| 21–26 | Thesis Chapters 5–6 + submit journal paper | |
