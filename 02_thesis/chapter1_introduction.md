# Chapter 1 — Introduction
## Thesis: Moving Target Defense & Formal Authorization Verification
## for Securing Distributed Microservices Against Network Attacks
**Author:** Deidine Cheigeur | Draft v2.1 | June 2026

---

## 1.1 Background and Motivation

The last decade has witnessed a fundamental shift in how software systems are designed and deployed. The monolithic application — a single, unified program running on a single server — has been progressively replaced by the **microservices architecture**, in which an application is decomposed into dozens or hundreds of small, independently deployable services communicating over a network [Tanenbaum & Van Steen, 2023]. This architectural shift was driven by the need for independent scalability, continuous deployment, and organisational alignment between development teams and service boundaries.

Today, cloud-native microservices represent the dominant deployment model for enterprise software. According to the Cloud Native Computing Foundation (CNCF), over 96% of organisations use or evaluate Kubernetes, the dominant container orchestration platform, for production workloads [CNCF Survey, 2023: https://www.cncf.io/reports/cncf-annual-survey-2023/]. Services are containerised using Docker, orchestrated by Kubernetes, and their inter-service communication is increasingly managed through a service mesh layer such as Istio.

This architectural evolution has, however, introduced a fundamentally new and poorly understood security challenge. The security assumptions embedded in traditional network security models — a trusted interior separated from an untrusted exterior by a firewall — are violated by design in microservices architectures. There is no perimeter. Every service is simultaneously a potential attacker and a potential victim. The attack surface is distributed, dynamic, and grows with every new service added.

The consequences of this insecurity are not hypothetical. The SolarWinds attack of 2020 demonstrated how lateral movement through a distributed system — from an initial compromised build pipeline service to highly privileged internal services — could compromise thousands of organisations simultaneously [Pearlson et al., 2021: https://hbr.org/2021/02/lessons-from-the-solarwinds-hack]. The Capital One breach of 2019 demonstrated how a privilege escalation vulnerability in a cloud microservices deployment could expose the personal data of 100 million customers [Senate Banking Committee, 2019: https://www.banking.senate.gov/hearings/data-security-lessons-from-the-capital-one-breach].

Two fundamental security properties must be guaranteed in distributed microservices:

1. **Containment:** A compromised service must not be able to reach services it is not authorised to communicate with (lateral movement prevention).
2. **Minimal privilege:** No service must be able to acquire permissions beyond those explicitly granted to it (privilege escalation prevention).

Current approaches fail to provide these guarantees for three reasons, which form the motivation for this thesis.

---

## 1.2 Problem Statement

### Problem 1: Static Attack Surface Enables Trivial Reconnaissance

In Kubernetes, each service has a stable IP address (ClusterIP) and a fixed set of ports. An attacker who gains code execution in one container can trivially map the entire cluster using standard network scanning tools (nmap, masscan) within seconds. This reconnaissance provides the complete blueprint for lateral movement: which services exist, which ports they expose, and which services accept connections from the compromised service.

The fundamental asymmetry: an attacker needs to perform reconnaissance **once** and the map remains valid indefinitely. A defender who does not change the environment gives the attacker unlimited time to plan and execute an attack.

**This thesis proposes Moving Target Defense (MTD) to break this asymmetry** by continuously rotating service endpoints, forcing the attacker to repeat reconnaissance after every rotation.

### Problem 2: Authorization Policies Are Never Formally Verified

The Zanzibar model [Pang et al., 2019: https://www.usenix.org/conference/atc19/presentation/pang], implemented in open-source as Ory Keto [https://github.com/ory/keto], provides the authorization foundation for distributed microservices. It defines, for each service pair, which operations are permitted.

However, authorization policies are written by engineers as configurations and are never formally verified. A subtle logical error — for example, a transitive permission relationship that was not intended — can create a privilege escalation path: a chain of individually legitimate authorization checks that, combined, grants a service access it should never have.

As Anderson [2020: https://www.cl.cam.ac.uk/~rja14/book.html] documents, the Needham-Schroeder security protocol was published in 1978 and believed correct. Lowe discovered a fatal flaw in 1995 — 17 years later — using formal analysis. The flaw was invisible to all testing and code review. The same class of undetected vulnerability can exist in authorization policies.

**This thesis proposes formal verification using TLA+ [Lamport, 2002: https://lamport.azurewebsites.net/tla/book.html] to prove that deployed authorization policies satisfy two invariants: no privilege escalation and no lateral movement.**

### Problem 3: Anomaly Detection Relies Exclusively on Machine Learning

Every current intrusion detection system for cloud microservices uses machine learning [Sengupta et al., 2020: https://doi.org/10.1109/COMST.2020.2982955]. This creates three operational problems:

1. **Training data dependency:** ML models require labelled attack datasets that are rarely available in production environments.
2. **Black-box opacity:** When a neural network flags an alert, an operator cannot understand why. Explainability in security-critical contexts is not optional.
3. **Adversarial fragility:** Sophisticated attackers can craft inputs designed to evade ML classifiers [Goodfellow et al., 2015]. Statistical detectors are harder to evade because they are based on mathematical properties of traffic distributions, not pattern recognition.

**This thesis proposes statistical anomaly detection using Shannon entropy and CUSUM [Chandola et al., 2009: https://doi.org/10.1145/1541880.1541882] applied to Keto authorization request logs — achieving reliable detection with no ML, no training data, and transparent, auditable alert logic.**

---

## 1.3 Research Questions

This thesis addresses the following research questions:

**RQ1:** Does periodic rotation of Kubernetes service endpoints (Moving Target Defense) significantly increase the mean time an attacker requires to map and exploit the cluster, and at what rotation frequency does the disruption to legitimate service discovery become acceptable?

**RQ2:** Can Shannon entropy and CUSUM applied to Keto authorization request logs detect DDoS attacks and lateral movement with recall ≥ 90% and false positive rate ≤ 2%, without any machine learning or labelled training data?

**RQ3:** Can TLA+ model checking prove that a deployed Keto authorization policy satisfies the NoPrivilegeEscalation and NoLateralMovement invariants, and does formal verification discover policy flaws that escape testing and code review?

### Hypothesis

A distributed microservices system secured by the combination of (1) endpoint rotation MTD, (2) statistical authorization anomaly detection, and (3) formally-verified Zanzibar/Keto policies will prevent successful lateral movement and privilege escalation attacks with greater reliability than any single mechanism alone — without relying on machine learning.

---

## 1.4 Contributions

This thesis makes three original contributions to the field of distributed systems security:

**Contribution 1 — MTD Engine for Kubernetes (MKE):**
A Kubernetes controller, implemented in Python, that periodically rotates ClusterIP addresses, port assignments, and internal service names of microservices. Service discovery for legitimate clients is maintained through Keto relationship tuples, which serve as the dynamic service registry. This is the first MTD system that integrates endpoint rotation with a formally-specified authorization layer.

**Contribution 2 — Statistical Authorization Anomaly Detector (SAAD):**
A lightweight statistical detector that monitors Keto authorization request logs in real time. It computes Shannon entropy across the distribution of authorization targets and applies CUSUM to per-service-pair request rates. Alerts are generated when entropy drops by more than 40% (indicating DDoS concentration) or when CUSUM exceeds 5σ (indicating a slow-ramp attack or lateral movement probe). No machine learning is used at any stage.

**Contribution 3 — Formal Verification of Zanzibar Authorization Policies (FV-Zanzibar):**
A TLA+ specification of the Keto authorization model, including the tuple graph structure, the recursive check algorithm, and the mutation operations (tuple add/remove). Two safety invariants are specified and verified using TLC model checking: NoPrivilegeEscalation and NoLateralMovement. This is the first formal verification of Zanzibar-style authorization policies published in the academic literature.

---

## 1.5 Scope and Limitations

This thesis focuses on **intra-cluster security** — the security of service-to-service communication within a Kubernetes cluster or federation of clusters. External-facing security (API gateway authentication, TLS termination, user authentication) is out of scope.

The MTD evaluation is conducted on a testbed of up to 10 microservices running on a 3-node minikube cluster. Scaling behaviour for clusters of hundreds of services is discussed in Chapter 5 but not experimentally evaluated — this is identified as future work.

The TLA+ formal model covers the core Keto authorization model. The full implementation of Keto includes additional features (namespace resolution, wildcard matching) that are not fully modelled. Limitations of the formal model are documented in Chapter 3, Section 3.4.

---

## 1.6 Thesis Structure

| Chapter | Content |
|---------|---------|
| **Chapter 2** | Background and Literature Review: distributed systems, access control, MTD, formal methods, statistical detection |
| **Chapter 3** | Methodology: system architecture, threat model, design of MKE, SAAD, and FV-Zanzibar |
| **Chapter 4** | Experimental Results: MTD effectiveness, detector performance, TLA+ verification results |
| **Chapter 5** | Discussion: limitations, deployment considerations, future work |
| **Chapter 6** | Conclusion: summary of contributions, broader implications |

---

## References (Chapter 1)

- Anderson, R. (2020). *Security Engineering*, 3rd ed. Wiley. https://www.cl.cam.ac.uk/~rja14/book.html
- Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys*, 41(3). https://doi.org/10.1145/1541880.1541882
- CNCF (2023). Annual Survey. https://www.cncf.io/reports/cncf-annual-survey-2023/
- Lamport, L. (2002). *Specifying Systems*. Addison-Wesley. https://lamport.azurewebsites.net/tla/book.html
- Pang, R., et al. (2019). Zanzibar. *USENIX ATC*. https://www.usenix.org/conference/atc19/presentation/pang
- Sengupta, S., et al. (2020). A survey of MTD. *IEEE CSTUT*, 22(3). https://doi.org/10.1109/COMST.2020.2982955
- Tanenbaum, A. S., & Van Steen, M. (2023). *Distributed Systems*, 4th ed. https://www.distributed-systems.net/
