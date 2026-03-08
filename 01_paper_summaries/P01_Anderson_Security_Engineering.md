# P01 — Anderson, R. (2020). Security Engineering (3rd ed.)
**Chapters read:** 4 (Access Control), 7 (Distributed Systems), 13 (Network Attacks), 21 (Formal Methods)
**Date read:** Month 1, Week 2
**Free PDF:** https://www.cl.cam.ac.uk/~rja14/book.html

---

## Why I read this
Foundation book for the entire thesis. Covers the three pillars of my work:
access control, distributed system security, and formal methods.

---

## Chapter 4 — Access Control

Access control is the selective restriction of access to a resource.
Three classical models:

- **DAC (Discretionary AC):** Owner decides who accesses their objects. Flexible but hard to audit at scale. Used in Unix file permissions.
- **MAC (Mandatory AC):** System enforces policy centrally. No user override. Used in military (Bell-LaPadula model: no read up, no write down).
- **RBAC (Role-Based AC):** Users assigned to roles; roles assigned permissions. Scales well for organisations. Limitation: roles are static — cannot express "Alice can edit this because Bob shared it with her."
- **ReBAC (Relationship-Based AC):** Permissions depend on relationships between entities. Enables fine-grained, contextual policies. This is what Zanzibar/Keto implements.

**Key quote:** *"Access control is the most fundamental security mechanism. If it is wrong, nothing else matters."* (Ch. 4, p. 94)

**Relevance to thesis:** Chapter 4 motivates why ReBAC (Zanzibar/Keto) is the right model for distributed microservices. RBAC cannot capture the dynamic, service-to-service relationships that enable lateral movement.

---

## Chapter 7 — Distributed Systems Security

Key challenges Anderson identifies:
1. **Authentication at scale** — how does service A prove its identity to service B in a system with hundreds of services?
2. **Authorisation consistency** — if service A grants access based on a stale policy, attacks can slip through during the propagation window.
3. **Audit trails** — in distributed systems, events are spread across nodes and logs must be aggregated to reconstruct an attack.
4. **No central control point** — you cannot deploy a single security perimeter around a distributed system.

**Most important finding for my thesis:** Point 4. There is no perimeter in microservices. Security must be embedded in every service interaction — exactly what Zanzibar/Keto + MTD provide.

---

## Chapter 13 — Network Attacks

Anderson classifies attacks into:
- **Passive attacks:** Eavesdropping, traffic analysis. Hard to detect because no packets are modified.
- **Active attacks:** DDoS, session hijacking, MITM, replay attacks. Modify or inject traffic.
- **Insider attacks:** Privilege escalation, lateral movement. Most expensive attacks.

DDoS specifically: attacker controls a botnet, directs it to flood a target.
Three types: volumetric (bandwidth), protocol (state exhaustion), application-layer (HTTP flood).

**Relevance:** These are the three attack classes my thesis defends against (DDoS, lateral movement, privilege escalation).

---

## Chapter 21 — Formal Methods

Anderson argues that formal methods are *underused* in security because:
1. They are perceived as hard (require mathematical training)
2. They are perceived as slow (model checking takes time)
3. Many practitioners believe testing is sufficient

He refutes all three: TLA+ is learnable in weeks, modern model checkers are fast for realistic system sizes, and testing can never cover all interleavings of distributed events.

**Key example Anderson gives:** The Needham-Schroeder protocol was published in 1978 and believed secure. In 1995 — 17 years later — Lowe found a MITM attack using formal analysis. Testing never caught it.

**Relevance:** This example is in my Chapter 1 as motivation for formal verification of Keto authorization policies.

---

## Personal Notes

This book changed how I think about security. The key insight I will carry through my whole thesis: **security is a system property, not a component property.** Adding a firewall or an IDS does not make a system secure. Security must be designed into every interaction from the beginning. That is exactly what my three contributions do.
