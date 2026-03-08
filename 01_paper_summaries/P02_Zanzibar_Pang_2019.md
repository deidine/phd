# P02 — Pang et al. (2019). Zanzibar: Google's Consistent, Global Authorization System
**Venue:** USENIX Annual Technical Conference (ATC 2019)
**Authors:** Ruoming Pang, Márton Cáceres, et al. (Google)
**Date read:** Month 1, Week 3
**PDF:** https://www.usenix.org/conference/atc19/presentation/pang

---

## Why I read this
Zanzibar is the paper behind Ory Keto — my authorization platform.
I need to understand it deeply to formally verify its properties in Contribution 3.

---

## The Problem It Solves

Google has hundreds of services (Drive, Maps, Calendar, YouTube, Photos...).
Each service needs to check: "Can user X perform action Y on object Z?"
Before Zanzibar, each service had its own authorization logic → inconsistent, hard to maintain, buggy.

Zanzibar provides a **single, unified authorization service** for all of Google.

---

## The Data Model

Everything is a **tuple**: `(object, relation, subject)`

Examples:
```
(doc:thesis.pdf,   owner,  user:deidine)
(doc:thesis.pdf,   viewer, user:supervisor)
(folder:phd,       parent, doc:thesis.pdf)
(group:lab_members, member, user:deidine)
```

Authorization check algorithm (simplified):
```
can(user:deidine, view, doc:thesis.pdf)?
→ Does tuple (doc:thesis.pdf, viewer, user:deidine) exist?  → YES → ALLOW
→ OR: Is there a parent folder with viewer permission?       → check recursively
→ OR: Is deidine a member of a group with viewer access?    → check group membership
```

This recursive graph traversal is the core of Zanzibar.

---

## Key Technical Contributions

1. **External consistency via Zookies:** A "zookie" is a token encoding a timestamp. When a document is created, its zookie is returned. Future authorization checks use the zookie to ensure they read from a consistent snapshot — preventing TOCTOU (time-of-check/time-of-use) vulnerabilities.

2. **Leopard indexing:** Precomputes group membership for large groups (>500 members) to avoid deep recursive lookups at query time.

3. **Global scale:** Trillions of tuples, millions of checks/second, < 10ms p95 latency, 99.999% availability over 3 years.

---

## What Zanzibar Does NOT Do

This is the most important finding for my thesis:

**Zanzibar has no formal security verification.**

The paper proves *performance* and *consistency* properties rigorously.
It does **not** prove:
- That no privilege escalation path exists in the tuple graph
- That a compromised service cannot create tuples that grant itself unauthorized access
- That the recursive lookup algorithm terminates without cycles creating infinite permission chains

**This gap is my Contribution 3.**

---

## Connection to Ory Keto

Ory Keto (github.com/ory/keto) is the open-source implementation of Zanzibar.
It uses the same tuple model and the same check algorithm.
Policies are written in OPL (Ory Permission Language).

In my prototype, I:
1. Deploy Keto in Kubernetes
2. Define authorization policies as tuples (which service can call which)
3. Monitor authorization request logs for statistical anomalies (Contribution 2)
4. Formally verify the tuple graph in TLA+ (Contribution 3)

---

## Personal Notes

Reading this paper was the moment I understood why my thesis topic is genuinely novel. Google deployed this at planetary scale in 2019. Six years later, nobody has formally verified whether the authorization model itself has privilege escalation vulnerabilities. My TLA+ specification will be the first formal verification of Zanzibar-style policies. That is a real contribution.
