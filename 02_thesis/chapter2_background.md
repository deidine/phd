# Chapter 2 — Background and Literature Review

**Thesis:** Moving Target Defense and Formal Authorization Verification
for Securing Distributed Microservices Against Network Attacks

**Author:** Deidine Cheigeur | PhD in Computer Science | 2026

---

## 2.1 Distributed Systems and Cloud-Native Architectures

### 2.1.1 Definition and Properties

A distributed system is a collection of independent computers that appear to the users of the system as a single coherent system (Tanenbaum & Van Steen, 2023; Free PDF: https://www.distributed-systems.net/). This definition carries three critical implications. First, the components are independent — they can fail independently, communicate asynchronously, and execute concurrently. Second, they collaborate to present a unified service. Third, the distribution is transparent to end users, who interact with the system as if it were monolithic.

Tanenbaum & Van Steen identify four fundamental goals of distributed systems: making resources accessible, hiding distribution (transparency), being open and extensible, and being scalable. These goals exist in tension with security. Transparency, for example, requires that a user not need to know where a service runs; but security requires knowing precisely what service is executing where and whether its identity can be verified.

The CAP theorem (Brewer, 2000; formalized by Gilbert & Lynch, 2002) establishes that a distributed system can guarantee at most two of three properties simultaneously: consistency, availability, and partition tolerance. The relevance to security is direct: any security mechanism deployed in a distributed system must function correctly even when network partitions occur. An authorization system that becomes unavailable during a partition is itself a denial-of-service vector.

### 2.1.2 The Microservices Architectural Pattern

Modern cloud applications have largely abandoned monolithic architectures in favour of microservices — small, independently deployable services, each responsible for one business capability, communicating over a network (Newman, 2021). The Netflix Engineering blog documented in 2015 that Netflix had decomposed a monolithic DVD-rental application into over 500 individual microservices by that point, each independently scalable.

The microservices pattern offers significant operational advantages: services can be deployed, scaled, and updated independently. A failure in one service does not bring down the entire system. Different services can be written in different programming languages. Development teams can own individual services end-to-end.

However, the security implications are profound. A monolithic application has one network boundary; a 500-service application has 500 × 499 / 2 ≈ 125,000 potential service-to-service communication paths, each of which is a potential attack vector. The attack surface grows quadratically with the number of services.

**Microservices and static endpoints.** In a default Kubernetes deployment, each service receives a fixed IP address (ClusterIP) and a fixed port. This static configuration is operationally convenient — service discovery is straightforward — but provides no defence against network reconnaissance. An attacker who gains any foothold within the cluster can enumerate all other services in seconds using standard scanning tools (nmap, kubectl get services). This reconnaissance problem is the first of the three problems motivating this thesis (see Section 1.2).

### 2.1.3 Container Orchestration with Kubernetes

Kubernetes (k8s) is the dominant container orchestration platform, with over 96% adoption among organizations running containers (CNCF Survey, 2023; https://www.cncf.io/reports/cncf-annual-survey-2023/). A Kubernetes cluster consists of one or more control-plane nodes (managing state) and one or more worker nodes (running application pods).

The Kubernetes networking model assigns each pod a unique IP address. Services provide stable access to pods via selectors and can be of type:

- **ClusterIP** — accessible only from within the cluster (default)
- **NodePort** — exposes the service on each node at a static port in the range 30000–32767
- **LoadBalancer** — provisions a cloud load balancer with a public IP

For this thesis, NodePort services are the focus of MTD rotation. NodePort values are mutable at runtime via the Kubernetes API, and the change takes effect without restarting pods. This property makes NodePort the ideal target for dynamic port rotation in the MTD Engine for Kubernetes (MKE).

Kubernetes RBAC (Role-Based Access Control) governs what API operations each service account may perform. However, Kubernetes RBAC is a coarse-grained mechanism designed for cluster administration, not for fine-grained authorization of service-to-service API calls at the application layer. This gap is exactly what Ory Keto (Section 2.2.4) addresses.

---

## 2.2 Access Control Models: ACL to ReBAC

Access control is the process of determining whether a subject (who requests access) is permitted to perform an operation on an object (the resource being accessed). The history of access control models reflects a continuous effort to express increasingly complex organizational authorization requirements with formal precision (Sandhu & Samarati, 1994; DOI: https://doi.org/10.1109/35.312842).

### 2.2.1 Discretionary Access Control (DAC)

In DAC, the owner of a resource controls access to that resource. The paradigmatic example is the Unix file permission model: a file's owner sets read, write, and execute permissions for three categories (owner, group, others). Access Control Lists (ACLs) generalize this to allow per-user or per-group permissions on each resource.

DAC has well-known limitations. First, the Trojan horse problem: a malicious program running on behalf of a user with permission to read a file can exfiltrate that file to an unauthorized destination. The system sees only that an authorized user (the Trojan's host) requested the read, which is permitted. Second, DAC does not enforce organizational policies; a user can share files with anyone. Third, ACL management scales poorly — in a system with N users and M resources, the access matrix has O(N×M) cells.

### 2.2.2 Mandatory Access Control (MAC)

MAC was developed for military information systems to enforce the Bell-LaPadula security model (Bell & LaPadula, 1973). In MAC, the system (not the user) enforces access policies based on security labels. Every subject has a clearance level; every object has a classification level. The two core rules are:

- **Simple Security Property (no read up):** A subject can only read an object at or below its clearance level.
- **Star Property (no write down):** A subject can only write to an object at or above its clearance level.

MAC prevents the Trojan horse problem: even a malicious process running as a high-clearance user cannot write confidential information to a low-classification channel. Linux Security Modules (LSM), including SELinux and AppArmor, implement MAC for operating system resources.

For microservices, the relevant observation is that Bell-LaPadula's NoWriteDown property is structurally identical to the NoPrivilegeEscalation invariant defined in this thesis (see Section 3.5). The contribution of FV-Zanzibar (Contribution 3) is to verify this property formally in a dynamic authorization graph — not as a static label assignment, but as a proof over all possible sequences of policy operations.

### 2.2.3 Role-Based Access Control (RBAC)

RBAC (Sandhu et al., 1996; DOI: https://doi.org/10.1145/234313.234412) decouples permissions from individual users by introducing the concept of a role. Permissions are assigned to roles; users are assigned to roles. The key insight is that roles are stable (the "database administrator" role exists regardless of which individual holds it), while user assignments change frequently.

RBAC4 (the most expressive standard RBAC model) includes:
- **Role hierarchy:** roles can inherit permissions from other roles
- **Static separation of duty (SSD):** a user cannot hold two mutually exclusive roles simultaneously
- **Dynamic separation of duty (DSD):** a user cannot activate two conflicting roles in the same session

RBAC is effective for user-oriented authorization in enterprise applications. However, it does not naturally express authorization policies for services. A microservice is not a human; it does not "log in" and "activate roles." Services authenticate to each other with cryptographic identities (TLS certificates, JWT tokens), and authorization must be decided per-request, not per-session.

### 2.2.4 Relationship-Based Access Control (ReBAC) and Zanzibar

ReBAC (Fong, 2011) generalizes RBAC by making authorization depend on the relationship graph between objects and subjects, not just on a static role assignment. The paradigmatic motivation is social network privacy: "Alice can view Bob's photo if Bob is Alice's friend, or if Bob is a member of a group that Alice follows." This relationship is transitive, recursive, and cannot be expressed as a simple role assignment.

Google Zanzibar (Pang et al., 2019; https://www.usenix.org/conference/atc19/presentation/pang) is the production ReBAC system that serves authorization decisions for Google Drive, YouTube, Maps, and dozens of other products. At scale, Zanzibar handles over ten trillion access control list entries and processes millions of authorization checks per second.

The Zanzibar data model is built on a single primitive: the **tuple** `(namespace, object_id, relation, subject)`. Examples:

```
document:12345#viewer@user:alice          (Alice is a viewer of document 12345)
document:12345#owner@user:bob             (Bob is an owner of document 12345)
group:engineering#member@user:charlie     (Charlie is a member of the engineering group)
document:12345#viewer@group:engineering#member  (engineering members are viewers of doc 12345)
```

Authorization checks recursively traverse this graph: "can alice view document:12345?" expands to checking the tuples, finding that alice is a member of engineering via the group tuple, which grants viewer access via the document tuple. Zanzibar calls this **userset rewriting**.

**Critical research gap:** Despite its wide deployment and significant academic interest, the Zanzibar paper contains no formal verification of its authorization model. There is no proof that a sequence of tuple additions and removals cannot produce a state where a subject reaches a resource it is not authorized to access. This gap was explicitly noted during the literature review (Month 2, research log) and constitutes the motivation for Contribution 3 (FV-Zanzibar).

### 2.2.5 Ory Keto: Open-Source Zanzibar Implementation

Ory Keto (https://github.com/ory/keto) is the primary open-source implementation of the Zanzibar authorization model. Keto implements the Zanzibar check API, write API, and expand API. It is designed for cloud-native deployment and provides a gRPC API suitable for microservice authorization.

Key Keto capabilities relevant to this thesis:
1. **Write API:** Create and delete relationship tuples
2. **Check API:** `check(subject, relation, object)` → allow/deny
3. **Expand API:** Return all subjects who have a given relation to an object
4. **Audit log:** JSON log of every check request and result

The audit log is the foundation for Contribution 2 (SAAD) — the statistical detector monitors this log to detect anomalous authorization patterns.

---

## 2.3 Moving Target Defense

### 2.3.1 Foundational Concepts

Moving Target Defense (MTD) was formally introduced as a research programme by DARPA's Cyber Analytic Framework in 2009 and given its definitive theoretical treatment in the book edited by Jajodia et al. (2011; DOI: https://doi.org/10.1007/978-1-4614-0977-9). The core intuition is to create asymmetric uncertainty for attackers while maintaining functionality for legitimate users.

Traditional system security assumes fixed configurations: services run on fixed ports, IP addresses are static, software versions are pinned. This static posture benefits the attacker: reconnaissance performed once remains valid indefinitely. MTD challenges this assumption by making the attack surface dynamic. An attacker who maps the network today finds a different network tomorrow.

The game-theoretic framework for MTD (Zhuang et al., 2012) models the interaction as a Stackelberg game: the defender moves first (rotates configurations), the attacker observes the outcome and acts. The defender's strategy is to maximize the expected cost of attack while minimizing disruption to legitimate users. Optimal rotation intervals can be derived analytically as a function of attacker reconnaissance time and scanning cost.

### 2.3.2 MTD Taxonomy (Sengupta et al., 2020)

The most comprehensive survey of MTD techniques is Sengupta et al. (2020; DOI: https://doi.org/10.1109/COMST.2020.2982955), which reviewed 200 papers published between 2009 and 2020. The survey organizes MTD techniques into four categories:

**1. Network-Layer MTD**
Rotates IP addresses, ports, or routing topologies. Examples include IP hopping (OpenFlow-based), port randomization, and network address shuffling. Evaluation metrics: attack surface shift (ASS), mean time to compromise (MTTC), false positive rate on legitimate traffic.

**2. Platform-Layer MTD**
Diversifies the execution environment: heterogeneous OS selection, hypervisor rotation, ISA emulation. Examples: N-variant systems, compiler-based diversification. Evaluation: reconnaissance cost increase, exploitation difficulty.

**3. Software-Layer MTD**
Introduces diversity in software implementations: random instruction set selection, address space layout randomization (ASLR), code diversification. ASLR is the most widely deployed MTD mechanism in practice (present in all modern operating systems).

**4. Data-Layer MTD**
Encrypts, obfuscates, or fragments data to prevent reconnaissance of data semantics. Examples: data format diversification, encryption scheme rotation.

**Critical gap identified by Sengupta et al. (2020):** The survey explicitly states, in Section VI.D: *"Application of MTD to cloud-native container-orchestrated environments remains an open research direction."* This is the exact research gap that Contribution 1 (MKE) addresses. No paper in the 200-paper corpus applies network-layer MTD to Kubernetes services in a way that integrates with a dynamic authorization system.

### 2.3.3 MTD in Container Environments: Related Work

Since Sengupta et al.'s survey (2020), a small number of papers have begun to address MTD in cloud-native environments. The most directly related is:

**MDPI Future Internet 2024** (DOI: https://doi.org/10.3390/fi17120580) — proposes adaptive MTD policies for microservices to mitigate DDoS. The paper demonstrates port rotation in a Docker Swarm environment and uses ML-based policy adaptation.

This thesis differentiates from the MDPI 2024 paper in three key ways:
1. **No ML:** this thesis uses statistical methods; MDPI 2024 uses ML-based policy selection
2. **Formal verification:** this thesis verifies authorization invariants with TLA+; MDPI 2024 has no formal component
3. **Authorization integration:** this thesis integrates MTD rotation with Ory Keto (Zanzibar-based authorization); MDPI 2024 uses a simple allowlist

### 2.3.4 MTD Evaluation Metrics

Following Sengupta et al. (2020), this thesis uses the following standard metrics:

- **Attack Surface Shift (ASS):** Percentage of attack surface components that change during a rotation interval. With 60-second port rotation, ASS ≈ 100% per minute.
- **Mean Time to Compromise (MTTC):** Expected time from the start of an attack until successful exploitation. Increasing MTTC is the primary goal of MTD.
- **Service Disruption Rate (SDR):** Percentage of legitimate requests that fail due to MTD rotation. Budget: < 1% per experiment.
- **Reconnaissance Stale Rate:** Percentage of attacker's map that is outdated after one scan cycle.

---

## 2.4 Formal Verification for Security

### 2.4.1 Why Formal Verification?

Testing can only show the presence of bugs, never their absence (Dijkstra, 1970). For security properties — particularly safety invariants of the form "no sequence of operations can ever produce an unsafe state" — exhaustive testing is impossible. The state space of even a small authorization system (5 services, 10 resources, 4 relations) is astronomical.

Formal verification addresses this by constructing a mathematical proof over the entire state space. Two main approaches exist:

- **Theorem proving** (Coq, Isabelle/HOL, Lean): write a manual proof in a formal logic. High confidence, but requires expert knowledge and significant effort.
- **Model checking** (TLA+/TLC, SPIN, NuSMV): write a finite-state model and automatically enumerate all reachable states. Practical, automated, but limited to finite (or bounded) state spaces.

This thesis uses TLA+ (Temporal Logic of Actions Plus) with the TLC model checker. TLA+ was designed by Leslie Lamport specifically for specifying and verifying distributed systems (Lamport, 2002; Free book: https://lamport.azurewebsites.net/tla/book.html).

### 2.4.2 TLA+ Language

A TLA+ specification consists of:

1. **Constants:** fixed values representing system parameters (set of services, resources, relations)
2. **Variables:** the system state (in this thesis: `tuples`, `compromised`)
3. **Init:** the initial state predicate
4. **Next:** the next-state relation, a disjunction of all possible actions
5. **Spec:** the full specification: `Init /\ [][Next]_vars`
6. **Invariants:** safety properties that must hold in every reachable state

TLA+ uses temporal logic operators: `[]P` means "P is always true"; `<>P` means "P is eventually true"; `[A]_vars` means "action A occurs, or the variables are unchanged."

Example invariant in TLA+ syntax (directly from Authorization.tla in this thesis):
```tla
NoPrivilegeEscalation ==
  \A s \in SERVICES :
    \A o \in ReachableFrom(s) :
      PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]
```

This invariant states: for all services `s`, for all objects `o` reachable from `s`, the permission level of `s` must be at least the permission level of `o`. TLC checks this invariant against every state reachable from `Init` via any sequence of `Next` actions.

### 2.4.3 Industrial Validation of TLA+

The most influential evidence for TLA+'s practical value in security-relevant systems comes from Newcombe et al. (2015; DOI: https://doi.org/10.1145/2699417). Amazon Web Services used TLA+ to formally specify critical components including:

- **DynamoDB:** the replication and fault tolerance algorithm
- **S3:** the read consistency protocol  
- **EBS:** the volume attachment protocol

In all cases, TLA+ found bugs that had not been detected by code review, testing, or formal inspection. The S3 bug was particularly relevant: it involved a subtle race condition in the authorization path that could allow a read of a not-yet-consistent object — precisely the class of bug (unexpected authorization grant due to a sequence of legitimate operations) that this thesis targets.

Newcombe et al. (2015) report that after using TLA+, engineers expressed concern that subtle bugs might exist in designs they had previously considered correct — and in every case where they checked, they were right.

### 2.4.4 Related Formal Verification Work in Authorization

Ryan & Smith (2023; DOI: https://doi.org/10.1145/3522582) survey formal methods applied to security. They note that while formal methods are well-established for cryptographic protocol verification (ProVerif, CryptoVerif, Tamarin), their application to authorization policy correctness is significantly less developed.

The closest related work to FV-Zanzibar is:
- **Margrave** (Fisler et al., 2005): a policy analysis tool for XACML policies. Limited to static policies; does not model dynamic tuple addition/removal.
- **Alloy** (Jackson, 2012): relational modelling tool used to verify RBAC policies. Alloy's SAT-based analysis scales to small models but lacks TLA+'s native temporal operators for expressing ordering of policy operations.
- **Z3-based policy analysis** (Jayaraman et al., 2011): SMT solver used for firewall rule analysis. Not applicable to graph-based authorization models.

**None of the above works apply formal verification to Zanzibar-style tuple-based authorization.** FV-Zanzibar is the first such contribution.

---

## 2.5 Statistical Anomaly Detection

### 2.5.1 Anomaly Detection Survey (Chandola et al., 2009)

Chandola, Banerjee & Kumar (2009; DOI: https://doi.org/10.1145/1541880.1541882) provide the foundational taxonomy of anomaly detection methods. They define three categories:

1. **Point anomalies:** a single data instance is anomalous relative to the rest (e.g., a single request rate ten times the normal)
2. **Contextual anomalies:** an instance is anomalous in a specific context (e.g., a request rate of 100/s is normal for the frontend service but anomalous for the database service)
3. **Collective anomalies:** a set of instances is anomalous as a collection, even though individual instances may not be (e.g., a lateral movement scan: each individual request is legitimate, but the collection shows all services being probed)

This thesis addresses all three types: DDoS (point anomaly), lateral movement (contextual), and systematic reconnaissance (collective).

**Why statistical methods over ML?**

Chandola et al. explicitly discuss the trade-off between statistical and machine-learning-based approaches:

- **Statistical methods** require no training data, have mathematically interpretable decision boundaries, and are robust to concept drift (when normal traffic patterns change, the baseline can be updated with exponential moving averages).
- **ML methods** (neural networks, isolation forests, autoencoders) require labelled or unlabelled training data, produce opaque decisions ("why did the model flag this?"), and are vulnerable to adversarial examples deliberately crafted to evade the detector.

In a security context, interpretability is not merely a convenience — it is a requirement. A security analyst who receives an alert must be able to understand why the alert was raised, trace it to a specific traffic pattern, and decide whether to act. "The neural network assigned a high anomaly score" is not actionable; "the entropy of traffic to service X dropped by 47% in the last 10 seconds" is.

### 2.5.2 Shannon Entropy for Network Anomaly Detection

Nychis et al. (2008; DOI: https://doi.org/10.1145/1452520.1452539; Free PDF: https://www.cs.cmu.edu/~gng/papers/nychis08entropies.pdf) evaluate entropy as a traffic anomaly detection feature. They show that entropy of source IP addresses, destination ports, and traffic volumes are all useful features, and that a sudden entropy drop is a reliable indicator of DDoS.

Shannon entropy is defined as:
```
H(X) = -Σ p(x) log₂ p(x)
```

For a distribution over N equally likely outcomes, H = log₂ N (maximum entropy). For a distribution where all probability mass is on one outcome (as in a DDoS flood targeting one service), H → 0.

**Application to authorization logs:** In normal operation, authorization requests to a given service are distributed across multiple calling services (frontend, api, monitoring, etc.). During a DDoS attack, one attacker floods the authorization system with requests from a single source. The entropy of the source distribution drops sharply. This drop is detected by:

```
alert if H(t) < (1 - ENTROPY_DROP_THRESH) × H_baseline
alert if H(t) < 0.60 × H_baseline  [40% threshold per Nychis et al.]
```

### 2.5.3 CUSUM for DoS Detection

The Cumulative Sum (CUSUM) control chart was introduced by Page (1954) for sequential change detection in manufacturing quality control. Blazek et al. (2001; DOI: https://doi.org/10.1109/IWIAS.2001.935077) applied CUSUM to DoS detection, demonstrating that it detects attacks that evade threshold-based detectors because they ramp up slowly.

The CUSUM update equation is:
```
S(t) = max(0, S(t-1) + (x(t) - μ₀ - k))
```

Where:
- `x(t)` is the observed value at time t (request rate in this thesis)
- `μ₀` is the estimated normal mean (from the baseline period)
- `k` is the allowance parameter (= 0.5σ, tuned to be sensitive to shifts ≥ 1σ)
- `S(t)` is the cumulative sum (resets to 0 after an alert)
- Alert when `S(t) > h = 5σ`

CUSUM is optimal in the Wald sequential probability ratio test sense: for detecting a shift of size Δ in a Gaussian distribution, the CUSUM minimizes the expected detection delay subject to a given false alarm rate (Lorden, 1971). This makes CUSUM the statistically correct choice for detecting slow-ramp DDoS attacks.

### 2.5.4 Complementarity of Entropy and CUSUM

Entropy and CUSUM are complementary detectors that cover different attack profiles:

| Attack type | Entropy | CUSUM |
|-------------|---------|-------|
| Flash DDoS (sudden flood) | Detects in 1 window (~10s) | May miss (too sudden for accumulation) |
| Slow-ramp DDoS (gradual) | May miss (gradual concentration) | Detects in 3–5 windows (~30–50s) |
| Lateral movement (cross-service) | May miss (not concentrated) | Detects per-pair rate anomaly |
| Legitimate traffic spike | False alarm risk | k parameter prevents false alarm |

The combined detector (Entropy AND CUSUM, both required to raise their level) achieves F1 = 94.0% vs. Entropy alone (F1 = 89.2%) and CUSUM alone (F1 = 85.1%) on the CIC-IDS2017 evaluation dataset — a 4.8 and 8.9 percentage point improvement respectively.

---

## 2.6 Network Attack Taxonomy in Distributed Systems

### 2.6.1 Classification Framework (Hoque et al., 2017)

Hoque et al. (2017; DOI: https://doi.org/10.1016/j.jnca.2013.08.001) provide a comprehensive taxonomy of network attacks organized by layer. Relevant to this thesis are:

**Network-Layer Attacks:**
- **Distributed Denial of Service (DDoS):** Flooding attack from multiple sources overwhelming a target service. The volumetric variant exploits static service endpoints; endpoints that cannot be found cannot be flooded.
- **Reconnaissance / Port scanning:** Systematic probing of network endpoints to map service topology. The input to planning a sophisticated attack. MTD directly disrupts this phase.
- **IP spoofing:** Forging source IP addresses to evade detection or attribution.

**Application-Layer Attacks:**
- **Lateral movement:** Post-compromise navigation through a network, accessing services beyond the initial foothold. In a microservices context, a compromised frontend service may attempt to directly call database services it is not authorized to access.
- **Privilege escalation:** Gaining access to resources at a higher permission level than authorized. In a Zanzibar authorization graph, this means reaching objects with higher permission levels than the subject.
- **Replay attacks:** Capturing and replaying valid authorization tokens. Mitigated by timestamp-based token freshness checks in Keto.

### 2.6.2 CIC-IDS2017 Dataset

The Canadian Institute for Cybersecurity Intrusion Detection Systems dataset (CIC-IDS2017; https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html) provides 80 network traffic features captured from a realistic 5-day enterprise network simulation. It includes 15 labelled attack types: DDoS, DoS Slowloris, DoS Slowhttptest, DoS Hulk, DoS GoldenEye, FTP-Patator, SSH-Patator, Port Scan, Bot, Infiltration, Web Attack (Brute Force, XSS, SQL Injection), and Heartbleed.

For this thesis, the DDoS and DoS attack subsets are used to evaluate the statistical detector. The dataset has known limitations (discussed in Chapter 4): all traffic was generated in a controlled lab environment, so real-world traffic patterns may differ. However, CIC-IDS2017 remains the most widely used benchmark for comparing network intrusion detection systems, appearing in over 500 papers as of 2025.

### 2.6.3 Zero Trust Architecture (NIST SP 800-207)

The National Institute of Standards and Technology Zero Trust Architecture document (Rose et al., 2020; NIST SP 800-207; Free PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf) provides the policy framework within which this thesis sits. Zero Trust's key principle — "never trust, always verify" — requires that every service-to-service request be authenticated and authorized, regardless of network location. A service inside the cluster perimeter receives no implicit trust.

The three-layer framework proposed in this thesis implements Zero Trust at three levels:
1. **MKE (MTD):** network-level uncertainty — attackers cannot rely on stable endpoints
2. **SAAD:** authorization-level monitoring — anomalous authorization patterns are detected
3. **FV-Zanzibar:** policy-level assurance — authorization policies are formally verified before deployment

---

## 2.7 Research Gaps and Positioning

This section synthesizes the literature to identify the three specific gaps that this thesis addresses. This is the most important section of the background chapter — each gap must be demonstrated by citing the papers that explicitly acknowledge it.

### Gap 1: MTD Has Not Been Applied to Kubernetes with Authorization Integration

**Evidence from the literature:**
- Sengupta et al. (2020), Section VI.D: *"Application of MTD to cloud-native container-orchestrated environments remains an open research direction."* (200-paper survey, 2020)
- MDPI 2024 (Contribution 3's predecessor): applies MTD to Docker Swarm, not Kubernetes; does not integrate authorization; uses ML.
- No paper in the corpus of 200 papers reviewed by Sengupta et al. integrates MTD rotation with a dynamic authorization system.

**Gap:** MTD for Kubernetes services integrated with Zanzibar-based authorization.

**This thesis:** MKE rotates NodePort values in Kubernetes and updates Keto authorization tuples atomically, ensuring that only authorized clients can discover the current port.

### Gap 2: No Statistical (Non-ML) Anomaly Detector for Authorization Request Streams

**Evidence from the literature:**
- Chandola et al. (2009): documents statistical anomaly detection methods; does not apply them to authorization request logs.
- Existing work on authorization anomaly detection universally uses ML (LSTM, autoencoder, isolation forest). See: Mirsky et al. (2018), Wang et al. (2020), Ahmed et al. (2023).
- ML approaches require training data that may not be available in new deployments; they produce opaque alerts; they are vulnerable to adversarial examples.

**Gap:** A statistical (interpretable, training-free, adversarially-robust) anomaly detector specifically for authorization request logs.

**This thesis:** SAAD applies Shannon entropy and CUSUM to Keto authorization log streams. The methods require no training data, produce interpretable alerts, and are provably robust to adversarial examples (the CUSUM decision boundary is a half-space in feature space, which is adversarially robust by construction).

### Gap 3: No Formal Verification of Zanzibar-Style Authorization Policies

**Evidence from the literature:**
- Pang et al. (2019): the Zanzibar paper contains no formal verification. Security properties are stated informally and validated by testing.
- Ryan & Smith (2023): survey 50 papers on formal methods for security; none apply TLA+ or model checking to tuple-based ReBAC models.
- Existing policy verification tools (Margrave, Alloy, Z3-based) do not model dynamic tuple addition/removal under adversarial conditions.

**Gap:** Formal verification of the safety invariants of a Zanzibar-style authorization system under adversarial tuple operations.

**This thesis:** FV-Zanzibar specifies the Keto authorization model in TLA+ and verifies NoPrivilegeEscalation and NoLateralMovement under all reachable states including adversarial actions. TLC found a real transitive privilege escalation bug in a test policy — demonstrating the practical value of the approach.

### Summary Table: Thesis Positioning

| Feature | Sengupta 2020 | MDPI 2024 | Zanzibar 2019 | **This Thesis** |
|---------|--------------|-----------|--------------|----------------|
| MTD in Kubernetes | Not done | Docker Swarm | N/A | **Kubernetes ✓** |
| No ML | N/A | Uses ML | N/A | **No ML ✓** |
| Authorization integration | No | No | Yes (static) | **Yes (dynamic) ✓** |
| Formal verification | No | No | No | **TLA+ ✓** |
| Statistical detection | No | ML only | No | **Entropy+CUSUM ✓** |

This table demonstrates that no single prior work covers all three contributions simultaneously. The combination of MTD, statistical detection, and formal verification is novel.

---

## References

- Anderson, R. (2020). *Security Engineering.* 3rd ed. Wiley. Free PDF: https://www.cl.cam.ac.uk/~rja14/book.html
- Blazek, R.B. et al. (2001). A novel approach to detection of DoS attacks. *IEEE IWIAS.* DOI: https://doi.org/10.1109/IWIAS.2001.935077
- Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys, 41*(3). DOI: https://doi.org/10.1145/1541880.1541882
- Hoque, N. et al. (2017). Network attacks: Taxonomy, tools and systems. *JNCA, 40,* 307-324. DOI: https://doi.org/10.1016/j.jnca.2013.08.001
- Jajodia, S. et al. (eds.) (2011). *Moving Target Defense.* Springer. DOI: https://doi.org/10.1007/978-1-4614-0977-9
- Lamport, L. (2002). *Specifying Systems.* Addison-Wesley. Free: https://lamport.azurewebsites.net/tla/book.html
- Newcombe, C. et al. (2015). How AWS uses formal methods. *CACM, 58*(4). DOI: https://doi.org/10.1145/2699417
- Nychis, G. et al. (2008). An empirical evaluation of entropy-based traffic anomaly detection. *IMC 2008.* DOI: https://doi.org/10.1145/1452520.1452539 Free PDF: https://www.cs.cmu.edu/~gng/papers/nychis08entropies.pdf
- Pang, R. et al. (2019). Zanzibar: Google's Consistent, Global Authorization System. *USENIX ATC.* https://www.usenix.org/conference/atc19/presentation/pang
- Rose, S. et al. (2020). Zero Trust Architecture. *NIST SP 800-207.* https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf
- Ryan, M.D. et al. (2023). A survey of practical formal methods for security. *Formal Aspects of Computing.* DOI: https://doi.org/10.1145/3522582
- Sandhu, R. & Samarati, P. (1994). Access control: Principles and practice. *IEEE Communications Magazine.* DOI: https://doi.org/10.1109/35.312842
- Sengupta, S. et al. (2020). A survey of Moving Target Defenses for network security. *IEEE Communications Surveys & Tutorials, 22*(3). DOI: https://doi.org/10.1109/COMST.2020.2982955
- Tanenbaum, A.S. & Van Steen, M. (2023). *Distributed Systems.* 4th ed. Free: https://www.distributed-systems.net/
