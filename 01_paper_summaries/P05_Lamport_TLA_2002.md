# P05 — Lamport, L. (2002). Specifying Systems: The TLA+ Language and Tools
**Publisher:** Addison-Wesley
**Author:** Leslie Lamport (Microsoft Research / Turing Award winner)
**Date read:** Month 2, Week 3
**Free PDF:** https://lamport.azurewebsites.net/tla/book.html
**TLA+ Toolbox:** https://lamport.azurewebsites.net/tla/toolbox.html
**VS Code extension:** search "TLA+ Nightly" in VS Code marketplace

---

## Why I read this
TLA+ is the formal specification language I use for Contribution 3.
Lamport is its creator. Chapters 1–3 are required reading.

---

## What is TLA+?

TLA+ (Temporal Logic of Actions) is a formal language for specifying concurrent
and distributed systems. It describes systems as:
- A set of **variables** (the state)
- An **Init** predicate (initial state)
- A **Next** action (how state transitions happen)
- **Invariants** (properties that must hold in every reachable state)
- **Temporal properties** (properties about sequences of states)

The key tool is **TLC** — the TLA+ model checker — which exhaustively
explores all reachable states and verifies that invariants hold.

**Links:**
- TLA+ home: https://lamport.azurewebsites.net/tla/tla.html
- TLC documentation: https://lamport.azurewebsites.net/tla/tlc.html
- Video course (free, by Lamport): https://lamport.azurewebsites.net/video/videos.html

---

## Key Concepts I Use

**State:** A mapping from variable names to values.
```tla
VARIABLES tuples, subjects, resources
```

**Initial state:**
```tla
Init == tuples = {} /\ subjects = {"svc_a", "svc_b"} /\ resources = {"db", "cache"}
```

**Action (transition):**
```tla
AddTuple(s, r, rel) ==
  /\ tuples' = tuples ∪ {<<s, rel, r>>}
  /\ UNCHANGED <<subjects, resources>>
```

**Invariant:**
```tla
NoPrivilegeEscalation ==
  ∀ s ∈ subjects, r ∈ resources :
    CanAccess(s, r) => IsAuthorised(s, r)
```

**Running TLC:** Explores all states reachable from Init via Next.
If NoPrivilegeEscalation is violated in any reachable state,
TLC returns a counterexample trace showing exactly how to reach it.

---

## Most Important Chapter for My Thesis

**Chapter 5 — Safety and Liveness.**
- **Safety property:** "Something bad never happens" → NoPrivilegeEscalation, NoLateralMovement
- **Liveness property:** "Something good eventually happens" → authorized requests eventually succeed

My two invariants are both safety properties.

---

## Learning Curve

Lamport estimates 2–3 weeks to become productive with TLA+.
My experience: 4 weeks to write my first complete spec, 6 weeks to write confidently.
The hardest part: thinking in terms of state machines rather than sequential code.

---

## Personal Notes

Reading Lamport changed how I think about programming. Every distributed system is a state machine — we just don't usually write it down explicitly. When you force yourself to write the state machine in TLA+, bugs become obvious because you have to specify exactly what can happen in every state. For security this is invaluable: you cannot accidentally leave an authorization bypass in a spec that you are required to state as a complete transition system.
