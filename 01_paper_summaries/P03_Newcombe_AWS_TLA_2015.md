# P03 — Newcombe et al. (2015). How Amazon Web Services Uses Formal Methods
**Venue:** Communications of the ACM, 58(4), 66–73
**Date read:** Month 1, Week 3
**DOI:** https://doi.org/10.1145/2699417

---

## Why I read this
This paper justifies my choice of TLA+ for Contribution 3.
If Amazon uses it in production to find real bugs, my thesis using it is credible.

---

## The Core Claim

Amazon engineers used TLA+ to specify and verify real distributed systems
(S3, DynamoDB, EBS, internal lock services) and found **bugs that no amount
of testing would have discovered.**

This is a practitioner paper — not theoretical. Real engineers, real systems, real bugs found.

---

## What TLA+ Found at AWS

| System | Bug Found | Consequence if shipped |
|--------|-----------|----------------------|
| DynamoDB replication | Race condition in leader election under specific network partition | Data loss under rare failure scenario |
| S3 | Authorization check could be bypassed after object ACL update during replication lag | Temporary unauthorized access to private objects |
| Internal lock service | Deadlock after exactly 14 specific concurrent operations | Full service hang requiring manual restart |

None of these were found by:
- Unit testing
- Integration testing
- Stress testing
- Code review

They were only found by TLA+ model checking — which exhaustively explores all possible system states.

---

## Why Testing Cannot Find These Bugs

Distributed systems have **combinatorial state spaces**. For N concurrent processes each with K possible states, there are K^N possible global system states. Testing samples a tiny fraction. Model checking explores all of them.

The S3 authorization bug required a specific sequence of: (1) ACL update, (2) network partition, (3) read request arriving during replication lag — with exact timing. In testing, this sequence never occurred by chance in 10,000 test runs. TLA+ found it in 3 minutes.

---

## How TLA+ Works (from this paper)

1. **Write a spec:** Describe system state as variables and transitions as actions
2. **Write invariants:** State properties that must always be true (e.g., "no unauthorized read ever returns data")
3. **Run TLC:** The model checker explores all reachable states
4. **Result:** Either "invariant holds in all states" (proof) or a counterexample trace

The engineers report the learning curve is about 2–3 weeks to become productive.

---

## Relevance to My Thesis

I apply the same approach to Keto/Zanzibar authorization:

1. **Spec:** Model the Keto tuple graph and the check algorithm in TLA+
2. **Invariants:**
   - `NoPrivilegeEscalation`: No subject can reach a resource above their permission level
   - `NoLateralMovement`: A compromised service cannot self-grant access to other services
3. **TLC:** Run the model checker on my testbed's policy set
4. **Result:** Proof that the policies I deploy are free of the two attacks

---

## Personal Notes

This paper completely changed my view of testing. Before reading it, I thought "if tests pass, the system is correct." After reading it, I understand that testing finds the bugs you thought to look for. Formal methods find the bugs you didn't know existed. For a security system, the unknown bugs are the dangerous ones.

Quote I will use in my thesis introduction:
> "We have found TLA+ to be surprisingly useful: engineers have used it to find subtle bugs, and TLA+ has given us more confidence in the correctness of our systems than any amount of testing could." (Newcombe et al., 2015)
