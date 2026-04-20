# P13 — Zero Trust Architecture
## Rose, S., Borchert, O., Mitchell, S., Connelly, S. (NIST SP 800-207, 2020)

**Free PDF:** https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf
**NIST page:** https://doi.org/10.6028/NIST.SP.800-207
**Institution:** National Institute of Standards and Technology, U.S. Department of Commerce

---

## Why This Paper Matters to My Thesis

NIST SP 800-207 provides the policy framework that validates the entire design philosophy of this thesis. The thesis implements Zero Trust at three levels: network (MTD), authorization (Keto + SAAD), and policy correctness (FV-Zanzibar). Citing NIST SP 800-207 situates the thesis within the most widely adopted enterprise security framework and provides official government endorsement for the design principles used.

---

## Key Concepts

### The Core Zero Trust Principle

Traditional perimeter security assumes that everything inside the network boundary is trusted; Zero Trust (ZT) assumes the opposite: **never trust, always verify.** The perimeter is assumed to already be breached. Every resource access request must be authenticated and authorized as if it originates from an untrusted network.

The seven tenets of Zero Trust (Section 2, p.7):

1. All data sources and computing services are considered resources
2. All communication is secured regardless of network location
3. Access to individual enterprise resources is granted on a per-session basis
4. Access to resources is determined by dynamic policy
5. The enterprise monitors and measures the integrity and security posture of all owned assets
6. All resource authentication and authorization is dynamic and strictly enforced before access is allowed
7. The enterprise collects as much information as possible about the current state of assets, network infrastructure and communications

**Thesis alignment with ZT tenets:**

| ZT tenet | Thesis implementation |
|----------|----------------------|
| Per-session authorization (tenet 3) | Keto checks every service-to-service call |
| Dynamic policy (tenet 4) | Keto tuples are updated by MKE on rotation |
| Continuous monitoring (tenet 5) | SAAD monitors authorization logs in real time |
| Dynamic, strict enforcement (tenet 6) | Keto denies all unconfigured calls by default |

### Zero Trust Architecture Components (Section 3)

NIST defines three core ZTA components:

1. **Policy Engine (PE):** Makes access decisions based on policy and contextual information. → **Ory Keto** in this thesis
2. **Policy Administrator (PA):** Communicates access decisions to Policy Enforcement Points. → **MKE** updates Keto as part of MTD rotation
3. **Policy Enforcement Point (PEP):** Enables, monitors, and terminates connections between subjects and enterprise resources. → **Kubernetes Network Policy + mTLS** in this thesis

### Microsegmentation

Section 3.2: "Microsegmentation creates secure zones in data centers and cloud deployments that allow security teams to isolate workloads from one another and secure them individually."

In Kubernetes, microsegmentation is implemented via:
- **Network Policies:** limit which pods can reach which other pods at the IP/port level
- **Service accounts:** each service runs with a dedicated identity
- **Keto authorization:** application-level authorization on top of network-level controls

The thesis builds on microsegmentation (implemented via Kubernetes Network Policies in the testbed) and adds the Keto authorization layer on top.

### Zero Trust for Microservices (Section 4.3)

NIST explicitly addresses microservices (Section 4.3, p.21): "Microservice-based applications break up an application into multiple small components that communicate over API calls. Each of these components needs to be treated as a separate resource and have separate authorization controls applied."

This section explicitly validates the design choice to place authorization at the service mesh / Keto level rather than relying on Kubernetes RBAC alone. Kubernetes RBAC governs cluster administration; Keto governs service-to-service API authorization.

---

## Gaps and Open Problems (Section 5)

NIST SP 800-207 identifies several open challenges in ZT deployment:

1. **Authorization policy correctness:** "Organizations should verify that their Zero Trust policies do not contain logical errors that could grant unintended access." (p.36) — This is exactly what FV-Zanzibar addresses.

2. **Monitoring:** "Continuous monitoring of authorization decisions is required to detect anomalous access patterns." (p.37) — This is what SAAD implements.

3. **Dynamic policy management:** "Policies must be updated as the system evolves, and these updates must not introduce new vulnerabilities." (p.38) — MKE updates Keto policies dynamically and FV-Zanzibar verifies them before deployment.

---

## Key Quotes

- "Zero Trust is a security model, a set of system design principles, and a coordinated cybersecurity and system management strategy based on an acknowledgment that threats exist both inside and outside traditional network boundaries." (p.2)
- "The enterprise should treat all subject credentials as potentially compromised and require continuous verification." (p.8)
- "Dynamic policy — including the observable state of identity, application/service, and the requesting asset — and may include behavioral and environmental attributes." (p.7)

---

## Citation Context in Thesis

Chapter 2, Section 2.6.3: NIST SP 800-207 is cited to position the three-layer framework within the Zero Trust architecture framework. Specifically:
- MKE implements ZT tenet 6 (dynamic, strict enforcement via dynamic endpoints)
- SAAD implements ZT tenet 5 (continuous monitoring)
- FV-Zanzibar addresses the policy correctness challenge in NIST Section 5
