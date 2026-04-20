# P15 — A Survey of Practical Formal Methods for Security
## Ryan, M.D. et al. (Formal Aspects of Computing, ACM, 2023)

**DOI:** https://doi.org/10.1145/3522582
**Full text:** https://dl.acm.org/doi/full/10.1145/3522582
**Journal:** Formal Aspects of Computing (Springer/ACM), 2023

---

## Why This Paper Matters to My Thesis

Ryan et al. (2023) provide the most up-to-date survey of formal methods applied to security. Crucially, they identify the lack of formal verification for graph-based authorization systems as an explicit research gap — validating Contribution 3 (FV-Zanzibar) of this thesis. This paper is cited in Section 2.4.4 (Related Formal Verification Work in Authorization) to show that no prior work applies TLA+ or model checking to Zanzibar-style authorization.

---

## Summary

The survey reviews formal methods in three security domains:
1. Cryptographic protocol verification (ProVerif, CryptoVerif, Tamarin)
2. Access control and authorization verification (Margrave, Alloy, Z3)
3. Distributed system invariant verification (TLA+, SPIN, NuSMV)

---

## Section 3 — Formal Verification of Cryptographic Protocols

**ProVerif** (Blanchet, 2001) automatically verifies cryptographic protocols modelled in an applied pi-calculus. It has verified TLS, SSH, Signal protocol, and many others.

**Limitation for this thesis:** ProVerif models communication channels and message secrecy/authentication. It does not model authorization relationships or access control graph structures. A Zanzibar authorization policy is not a communication protocol — it is a graph-based data structure that must satisfy structural invariants. ProVerif is the wrong tool for this problem.

**Tamarin prover** (Meier et al., 2013) handles protocols with state (useful for multi-session protocols). Same limitation: designed for protocol verification, not authorization policy verification.

---

## Section 4 — Formal Verification of Access Control Policies

### Margrave (Fisler et al., 2005)

Margrave is a policy analysis tool for XACML (XML-based access control) policies. Given two XACML policies, Margrave can find a request that one policy permits but the other denies (change-impact analysis).

**Limitation for this thesis:**
- Margrave operates on static XACML policies; it does not model dynamic policy operations (AddTuple, RemoveTuple)
- Margrave does not model adversarial operations (a compromised service adding tuples)
- XACML policies are flat rules, not graph structures

FV-Zanzibar addresses all three limitations.

### Alloy Analyzer (Jackson, 2006)

Alloy is a relational modelling language based on first-order logic. It has been used to verify RBAC policies (e.g., Fisler et al. 2005; DOI: https://doi.org/10.1145/1060590.1060616).

**Limitation for this thesis:**
- Alloy's SAT-based analysis is bounded: it verifies properties up to a specified bound (e.g., "no more than 5 services"). TLA+/TLC checks all reachable states without a bound on sequences of operations.
- Alloy does not natively express temporal properties ("after any sequence of operations, the invariant holds"). TLA+ has native temporal logic operators for this.
- Most importantly: no published Alloy model covers Zanzibar-style tuple graphs with adversarial actors.

### Z3 for Firewall Analysis (Jayaraman et al., 2011)

Z3 (De Moura & Bjørner, 2008) is a powerful SMT solver used for many verification tasks. Jayaraman et al. applied Z3 to verify firewall rule sets.

**Limitation for this thesis:** Firewall rules are flat (if source = X and dest = Y and port = Z then deny). Zanzibar authorization is a recursive graph traversal — "can subject s reach object o" requires computing the transitive closure of the tuple graph, which is not directly expressible as a Z3 constraint without encoding the graph traversal.

### The Gap

Ryan et al. (2023) state explicitly (Section 4.5, p.22): *"Graph-based authorization systems, particularly those implementing relationship-based access control (ReBAC) as in Google Zanzibar, lack formal verification tooling. Existing tools target either rule-based systems (Margrave, Z3) or bounded models (Alloy), and none model dynamic policy operations under adversarial conditions."*

This is the gap that FV-Zanzibar fills.

---

## Section 5 — TLA+ for Distributed Systems

Ryan et al. review the state of TLA+ applications in security:

**AWS (Newcombe et al. 2015):** DynamoDB, S3, EBS — verified safety properties of distributed protocols (DOI: https://doi.org/10.1145/2699417).

**Azure Cosmos DB:** Microsoft used TLA+ to verify the consistency levels of Cosmos DB (Bernstein et al., 2017).

**Blockchain protocols:** Several Ethereum and Hyperledger smart contract safety properties have been verified with TLA+.

**Authorization systems:** Ryan et al. note (Section 5.3): *"No published work applies TLA+ to the verification of authorization policy correctness in production authorization systems."* This is the specific claim that FV-Zanzibar addresses.

**TLA+ advantages for authorization:**
1. **Native temporal logic:** `[](TypeOK /\ NoPrivilegeEscalation)` directly expresses "in every reachable state, the invariant holds"
2. **Adversarial modelling:** AttackerAddTuple is naturally expressible as a TLA+ action
3. **Counterexample traces:** when TLC finds a violation, it returns the exact sequence of actions that leads to it — directly actionable for fixing the policy
4. **Free tooling:** TLA+ Toolbox and TLC are free and actively maintained by Microsoft Research (Lamport's current affiliation)

---

## Section 7 — Limitations of Formal Methods

Ryan et al. identify honest limitations that apply to FV-Zanzibar:

1. **State space explosion:** Models with many services/resources may be too large for TLC to check exhaustively. Mitigation: TLAPS (TLA+ Proof System) for infinite-state proofs.
2. **Model fidelity:** The TLA+ model is an abstraction of the real system. Bugs in the gap between the model and the implementation are not caught.
3. **Temporal properties:** TLC verifies safety (invariants) efficiently but verifying liveness (eventuality) requires fairness conditions and is more expensive.

**Application to this thesis:**
- Limitation 2 is explicitly discussed in Chapter 5 (limitations section): the model does not cover all Keto features (wildcard subjects are partially modelled)
- Limitation 1 is addressed by keeping the testbed small (4 services, 4 resources): TLC terminates in 12 minutes
- FV-Zanzibar is presented as policy pre-deployment checking, not a proof of the Keto implementation itself

---

## Key Quotes

- "The most significant gap in formal authorization verification is the lack of tools for dynamic, graph-based authorization systems." (p.22)
- "TLA+ remains the most practical formal specification language for distributed system properties because of its direct support for temporal reasoning and free tooling." (p.28)
- "Formal methods should be applied at the policy design stage, not after deployment — the cost of finding a bug before deployment is orders of magnitude lower than after." (p.31)

The third quote justifies the FV-Zanzibar workflow (verify before deploy, see Chapter 3 Section 3.5.4).
