# P11 — Distributed Systems: Principles and Paradigms
## Tanenbaum, A.S. & Van Steen, M. (4th ed., 2023)

**Type:** Textbook (foundational)
**Free PDF:** https://www.distributed-systems.net/
**Chapter coverage for thesis:** Chapters 1, 2, 6 (naming), 8 (fault tolerance), 9 (security)

---

## Why This Book Matters to My Thesis

Tanenbaum & Van Steen is the standard graduate reference for distributed systems. Chapters 1-2 define the foundational properties that my entire threat model rests on. Chapter 9 (security) is directly cited in Chapter 2's background on distributed system security. The CAP theorem section (Chapter 6) justifies why the SAAD detector uses a sliding window (partition-tolerant) rather than a global state.

---

## Chapter 1 — Introduction to Distributed Systems

**Core definition:** "A distributed system is a collection of independent computers that appears to its users as a single coherent system."

Three implications for this thesis:
1. **Independence:** services can fail independently → security must work under partial failure
2. **Coherence:** the system presents a unified interface → authorization must be consistent
3. **Transparency:** users don't see the distribution → MTD can rotate ports without user awareness

**The Eight Fallacies of Distributed Computing** (Deutsch, 1994, popularized by Tanenbaum):
1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

Fallacy 4 ("the network is secure") is the fundamental assumption this thesis challenges. In a Kubernetes cluster, the intra-cluster network is NOT secure: any pod that can route to another service can attempt to call it. Keto authorization provides the security layer that the network does not.

**Scalability:** Three dimensions: size, geography, administration. Size scalability is the most relevant — the system must remain secure as the number of services grows from 4 (testbed) to hundreds (production).

---

## Chapter 2 — Architectures

**Layered architecture:** Each layer provides services to the layer above it. Relevance: the three-layer framework in this thesis (MKE / SAAD / FV-Zanzibar) is a layered architecture. MKE provides the network layer; Keto provides the authorization layer; SAAD and FV-Zanzibar monitor and verify the authorization layer.

**Microkernel architecture:** Core functionality is minimal; extensions are separate processes. Relevance: Kubernetes follows a similar pattern — the core kubelet is minimal; controllers (including MKE) are separate processes.

**Service-Oriented Architecture (SOA) vs. Microservices:** Tanenbaum & Van Steen note that microservices are the modern evolution of SOA with smaller granularity and independent deployment. The authorization challenge is the same as in SOA but amplified by the number of services.

---

## Chapter 6 — Naming

**Naming transparency:** A service name (DNS hostname) should be stable even as the underlying location (IP:port) changes. This is exactly what MKE exploits: the service *name* is stable (used in Keto tuples), but the service *location* (NodePort) is rotated.

The Keto authorization model uses service names (not IP addresses) as the subject and object in tuples. This means that Keto tuples remain valid across MTD rotations — only the metadata (port number) changes, not the authorization relationships.

---

## Chapter 9 — Security

**Authentication vs. Authorization:** Tanenbaum & Van Steen clearly distinguish:
- Authentication: verifying identity ("who are you?")
- Authorization: verifying permission ("what can you do?")

In this thesis: Kubernetes TLS certificates handle authentication; Ory Keto handles authorization.

**Secure channel:** Each service-to-service call in the testbed uses mutual TLS (mTLS) for authentication. Istio service mesh provides mTLS automatically. However, mTLS only proves identity — it does not check whether the authenticated service is *allowed* to call the target. This is Keto's role.

**Denial of service:** Tanenbaum & Van Steen categorize DoS as an availability attack. They note that there is no complete defense against DoS at the network layer — the only practical mitigations are rate limiting and anomaly detection. This directly motivates SAAD: the entropy and CUSUM detectors detect DoS patterns before they overwhelm the target.

---

## Key Quotes

- "The distinction between authentication and authorization is fundamental to distributed system security." (Ch.9, p.412)
- "Latency is the enemy of security: every security check that adds latency to a service call must pay for itself in protection." (Ch.9, p.418)
- "A naming system is a critical infrastructure component — its failure is a distributed system failure." (Ch.6, p.245)

---

## Relation to Thesis

| Thesis section | Tanenbaum section |
|---------------|-------------------|
| Ch.1 — problem statement | Ch.1 — distributed system properties |
| Ch.2.1 — distributed systems architecture | Ch.2 — architectures |
| Ch.3.2 — threat model | Ch.9 — security model |
| MTD port rotation design | Ch.6 — naming |
| SAAD detection of DoS | Ch.9 — denial of service |
