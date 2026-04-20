# P12 — Network Attacks: Taxonomy, Tools and Systems
## Hoque, N. et al. (Journal of Network and Computer Applications, 2017)

**DOI:** https://doi.org/10.1016/j.jnca.2013.08.001
**Journal:** Journal of Network and Computer Applications, Vol. 40, pp. 307-324, 2017

---

## Why This Paper Matters to My Thesis

This paper provides the taxonomic framework for classifying network attacks used in Chapter 2 (Section 2.6) of this thesis. The taxonomy is important because it allows each of the three thesis contributions to be positioned against a clear set of attack types: MTD targets reconnaissance, SAAD targets DDoS and lateral movement, FV-Zanzibar targets privilege escalation.

---

## Summary

Hoque et al. conduct a systematic review of 200+ papers on network attacks published between 2000 and 2012. They propose a four-level taxonomy:

```
Network Attacks
├── 1. Reconnaissance Attacks
│   ├── Passive (traffic sniffing, port scanning)
│   └── Active (port scanning, service enumeration, OS fingerprinting)
├── 2. Denial of Service Attacks
│   ├── Volumetric (ICMP flood, UDP flood, SYN flood)
│   ├── Protocol (Ping of Death, Teardrop)
│   └── Application-layer (HTTP flood, Slowloris, SlowHTTP)
├── 3. Penetration Attacks
│   ├── Privilege escalation (vertical: gaining higher access)
│   ├── Lateral movement (horizontal: spreading to other systems)
│   └── Data exfiltration (reading unauthorized data)
└── 4. Malware Attacks
    ├── Trojans, worms, ransomware
    └── Botnets (command & control)
```

---

## Key Attack Types Relevant to This Thesis

### Reconnaissance Attacks

**Port scanning:** Systematic probing of a host's port range to identify open services. Tools: nmap, masscan, zmap.

- nmap standard scan (`nmap -sV <target>`) checks all 65,535 ports at ~1,000 ports/second → 65 seconds for a full scan.
- With MTD at 60-second rotation: the attacker's first scan is complete, but the discovered ports are already stale.
- **This is the exact attack that MKE defeats.** Hoque et al.'s data: reconnaissance is the first phase of every attack kill-chain. Disrupting reconnaissance delays all subsequent attack phases.

**Service enumeration:** After port scan, attacker queries each open port to identify the running service and version. This allows exploit selection. MTD addresses this by making enumeration results stale before they can be used.

### Denial of Service Attacks

**Volumetric DDoS:** Attack sends a flood of traffic that saturates the target's bandwidth or CPU. In a microservices context, this typically targets the HTTP/gRPC endpoints of services rather than the network layer.

**Application-layer DoS (Slowloris, SlowHTTP):** Attack opens connections and sends requests slowly, holding connections open without completing them. This exhausts the server's connection pool. Hoque et al. note these attacks are harder to detect than volumetric attacks because per-connection traffic rates appear normal.

**Detection:** SAAD's CUSUM detector is specifically designed to detect slow-ramp attacks like Slowloris: the request rate from a specific source increases gradually, which CUSUM accumulates over time.

### Penetration Attacks

**Privilege escalation (vertical):** An attacker who gains access as a low-privilege service attempts to reach high-privilege resources. In the Zanzibar/Keto model, this means the compromised service adds authorization tuples that grant itself access to higher-PERMISSION_LEVEL objects. **FV-Zanzibar's NoPrivilegeEscalation invariant directly prevents this.**

**Lateral movement (horizontal):** After compromising one service, the attacker attempts to reach other services. In a Kubernetes cluster, this means the compromised pod begins making requests to services it was not originally intended to call. **SAAD's CUSUM detector identifies this as an anomalous per-pair request rate.**

---

## CIC-IDS2017 Attack Coverage

The CIC-IDS2017 dataset (https://www.unb.ca/crc/research/datasets/ids/CIC-IDS2017.html) covers these attack types from the taxonomy:

| Hoque taxonomy | CIC-IDS2017 label | This thesis defends against |
|----------------|-------------------|----------------------------|
| Reconnaissance | Port Scan | MKE (MTD) |
| Volumetric DDoS | DDoS (UDP, TCP, ICMP) | SAAD entropy |
| Slow DoS | DoS Slowloris, DoS GoldenEye | SAAD CUSUM |
| Brute force (credentials) | FTP-Patator, SSH-Patator | Out of scope |
| Web application attacks | SQL injection, XSS | Out of scope |
| Privilege escalation | Infiltration | FV-Zanzibar |

The thesis defends against 4 of 6 attack categories identified by Hoque et al. as relevant to microservices. Brute force and web application attacks are out of scope (they require different defence mechanisms — authentication hardening and WAF respectively).

---

## Key Quotes

- "Reconnaissance is universally the first phase of targeted attacks. No sophisticated attack proceeds without prior information gathering." (p.309)
- "Application-layer DoS attacks are the fastest-growing category because they are difficult to distinguish from legitimate traffic by volume alone." (p.315)
- "Lateral movement exploits the implicit trust between internal services. Most enterprise networks grant unrestricted internal communication, which is the attacker's key advantage." (p.318)

The quote on lateral movement directly motivates the zero-trust design of this thesis: Keto enforces authorization on every service-to-service call, even within the cluster.
