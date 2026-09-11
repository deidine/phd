-------------------------------- MODULE Authorization --------------------------------
(*
  TLA+ Formal Specification of Zanzibar/Keto Authorization Model
  Contribution 3 of PhD Thesis: Formal Verification of Authorization Policies

  Author: Deidine Cheigeur
  Date: 2026
  Reference:
    - Pang et al. (2019) Zanzibar: https://www.usenix.org/conference/atc19/presentation/pang
    - Ory Keto: https://github.com/ory/keto
    - Lamport TLA+: https://lamport.azurewebsites.net/tla/book.html
    - Newcombe et al. (2015): https://doi.org/10.1145/2699417

  Purpose:
    Formally verify that a Keto authorization policy — fixed as INITIAL_TUPLES,
    the policy as it would actually be deployed, not a hypothetical space of
    edits an admin could make — satisfies two safety invariants:
    1. NoPrivilegeEscalation: no service can reach (directly or transitively)
       a resource above its permission level, under the ORIGINAL policy.
    2. NoLateralMovement: a compromised service, using only "can_grant" rights
       the original policy actually gave it, cannot self-grant NEW access it
       didn't already have.

  This module declares CONSTANTS abstractly (SERVICES, RESOURCES, RELATIONS,
  PERMISSION_LEVEL, INITIAL_TUPLES) — it has no runnable model on its own.
  Concrete scenarios (a specific policy under test) live in Scenarios.tla,
  each paired with a .cfg file in this directory.

  How to run (TLC model checker), from this directory:
    java -jar <path-to>/tla2tools.jar -deadlock -config Baseline.cfg Scenarios.tla
    java -jar <path-to>/tla2tools.jar -deadlock -config TransitiveLogging.cfg Scenarios.tla
    java -jar <path-to>/tla2tools.jar -deadlock -config AdminCreep.cfg Scenarios.tla

  tla2tools.jar (official TLA+ tools release):
    https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar

  See results/README.md for actual, reproduced TLC output and results table.
*)

EXTENDS Sequences, FiniteSets, Naturals

CONSTANTS
  SERVICES,        \* e.g., {"svc_frontend", "svc_api", "svc_db", "svc_cache"}
  RESOURCES,       \* e.g., {"db_read", "db_write", "cache_read", "admin_api"}
  RELATIONS,       \* e.g., {"can_call", "can_read", "can_write", "owns"}
  PERMISSION_LEVEL, \* Function: SERVICES \cup RESOURCES -> Nat (privilege level)
                    \* e.g., svc_db -> 3, svc_frontend -> 1
  INITIAL_TUPLES   \* The concrete, already-decided Keto policy under test —
                   \* a fixed set of <<subject, relation, object>> triples.

VARIABLES
  tuples,          \* Set of <<subject, relation, object>> triples
  compromised      \* Set of services currently compromised (for attack simulation)

---------------------------------------------------------------------------

\* Type invariant: all tuples are valid triples
TypeOK ==
  /\ tuples \subseteq (SERVICES \X RELATIONS \X (SERVICES \cup RESOURCES))
  /\ compromised \subseteq SERVICES

\* Initial state: the policy under test, as actually configured in Keto —
\* NOT empty. This spec verifies one concrete, already-decided policy against
\* attacker behavior, not "could some hypothetical future admin action ever
\* misconfigure something" (that question is close to vacuous: AddTuple below
\* is unconstrained, so it can trivially construct almost any bad edge). The
\* thing worth model-checking is: given the policy as it will actually be
\* deployed, can an attacker who compromises a service reach further than
\* their level allows?
Init ==
  /\ tuples = INITIAL_TUPLES
  /\ compromised = {}

---------------------------------------------------------------------------
\* ACTIONS
---------------------------------------------------------------------------

\* Legitimate policy operation: admin adds an authorization tuple. Kept as a
\* named operator for documentation/future use (e.g. checking a *sequence* of
\* proposed policy edits against the invariants), but deliberately NOT part
\* of Next below — see the note on Init. Left fully unconstrained here on
\* purpose: it is not this spec's job to say which edits an admin *should*
\* make, only to check a given resulting policy.
AddTuple(subj, rel, obj) ==
  /\ subj \in SERVICES
  /\ obj  \in (SERVICES \cup RESOURCES)
  /\ rel  \in RELATIONS
  /\ tuples' = tuples \cup {<<subj, rel, obj>>}
  /\ UNCHANGED compromised

\* Legitimate policy operation: admin removes an authorization tuple. Also
\* not part of Next — see AddTuple's note.
RemoveTuple(subj, rel, obj) ==
  /\ <<subj, rel, obj>> \in tuples
  /\ tuples' = tuples \ {<<subj, rel, obj>>}
  /\ UNCHANGED compromised

\* Attack simulation: a service becomes compromised
CompromiseService(svc) ==
  /\ svc \in SERVICES
  /\ svc \notin compromised
  /\ compromised' = compromised \cup {svc}
  /\ UNCHANGED tuples

\* Attack simulation: a compromised service can write a new tuple for a
\* target ONLY if the ORIGINAL policy already granted it "can_grant" rights
\* over that exact target. In Zanzibar/Keto, "can_grant" (or "owns") is the
\* relation that lets a subject manage another object's tuples — it is not
\* something every service should hold. Gating on it here (rather than
\* letting a compromised service rewrite ANYTHING, which would model "the
\* attacker also has raw write access to Keto's admin API" and would break
\* every policy regardless of design) is what makes the result
\* policy-dependent: a service the policy never granted "can_grant" to gains
\* zero attacker-write capability when compromised — NoLateralMovement then
\* holds for it automatically. A policy that over-grants "can_grant" to an
\* ordinary service (the "wildcard over-grant" / "admin creep" bug classes)
\* is exactly the flaw this is meant to catch.
AttackerAddTuple(attacker, rel, target) ==
  /\ attacker \in compromised
  /\ <<attacker, "can_grant", target>> \in INITIAL_TUPLES
  /\ rel      \in RELATIONS
  /\ tuples'  = tuples \cup {<<attacker, rel, target>>}
  /\ UNCHANGED compromised

\* Next-state relation: with the policy fixed at INITIAL_TUPLES (see Init),
\* the only moves left to explore are attacker moves — compromising a
\* service, then that service trying to grant itself more access. AddTuple/
\* RemoveTuple are intentionally excluded: this spec checks one concrete
\* policy for attacker-reachable violations, not "the space of all policies
\* an admin could ever author."
Next ==
  \/ \E svc \in SERVICES : CompromiseService(svc)
  \/ \E a \in SERVICES, r \in RELATIONS, t \in (SERVICES \cup RESOURCES) :
       AttackerAddTuple(a, r, t)

---------------------------------------------------------------------------
\* HELPER FUNCTIONS
---------------------------------------------------------------------------

\* Check if subject has relation rel to object (direct lookup)
HasDirectRelation(subj, rel, obj) ==
  <<subj, rel, obj>> \in tuples

\* Objects directly reachable from a subject via one hop.
DirectlyReachable(subj) ==
  { obj \in (SERVICES \cup RESOURCES) :
      \/ <<subj, "can_call", obj>> \in tuples
      \/ <<subj, "can_read", obj>> \in tuples
      \/ <<subj, "can_write", obj>> \in tuples }

\* Transitive closure of DirectlyReachable, following chains through
\* intermediate SERVICES (a RESOURCE is always a leaf: AddTuple/AttackerAddTuple
\* only ever put a SERVICE in the subject position, so nothing points onward
\* from a RESOURCE). `visited` guards against cycles in the tuple graph.
\* This is what makes a bug like "frontend -> logger -> sensitive-db" —
\* where frontend has no *direct* tuple to the DB — actually detectable;
\* a non-transitive, one-hop-only reachability check cannot see it.
RECURSIVE ReachableFromVisited(_, _)
ReachableFromVisited(subj, visited) ==
  LET direct == DirectlyReachable(subj) \ visited
      nextHops == direct \cap SERVICES
  IN  direct \cup UNION { ReachableFromVisited(o, visited \cup direct) : o \in nextHops }

\* Reflexive: a subject can always trivially "reach" itself (zero hops) —
\* self-referential tuples (e.g. an attacker adding a harmless
\* subj->subj self-loop) must not register as gaining new access.
ReachableFrom(subj) == {subj} \cup ReachableFromVisited(subj, {subj})

\* Same closure, but computed against the ORIGINAL policy (INITIAL_TUPLES)
\* only — i.e. what a service was legitimately able to reach before any
\* compromise, ignoring anything an attacker has added since. INITIAL_TUPLES
\* is a CONSTANT, so this is a fixed quantity per model, not a moving target.
DirectlyReachableOriginal(subj) ==
  { obj \in (SERVICES \cup RESOURCES) :
      \/ <<subj, "can_call", obj>>  \in INITIAL_TUPLES
      \/ <<subj, "can_read", obj>>  \in INITIAL_TUPLES
      \/ <<subj, "can_write", obj>> \in INITIAL_TUPLES }

RECURSIVE ReachableFromOriginalVisited(_, _)
ReachableFromOriginalVisited(subj, visited) ==
  LET direct == DirectlyReachableOriginal(subj) \ visited
      nextHops == direct \cap SERVICES
  IN  direct \cup UNION { ReachableFromOriginalVisited(o, visited \cup direct) : o \in nextHops }

ReachableFromOriginal(subj) == {subj} \cup ReachableFromOriginalVisited(subj, {subj})

---------------------------------------------------------------------------
\* SAFETY INVARIANTS (what TLC will verify)
---------------------------------------------------------------------------

\*
\* INVARIANT 1: NoPrivilegeEscalation
\* A service can never reach a resource whose privilege level exceeds its own.
\*
\* Formal statement:
\*   For all services s and all objects o that s can reach UNDER THE ORIGINAL
\*   POLICY (INITIAL_TUPLES): PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]
\*
\* Deliberately checked against ReachableFromOriginal, not the live `tuples`
\* variable: this is meant as the pre-deployment "does the policy AS DESIGNED
\* have a flaw" check (FV-Zanzibar's stated purpose), independent of runtime
\* attacker behavior. Checking it against live `tuples` would make it fail
\* the instant ANY service is compromised in ANY system with more than one
\* privilege level, since AttackerAddTuple is unconstrained — that would be
\* testing "can an attacker try something bad" (trivially always yes), not
\* "is the policy itself sound." NoLateralMovement below covers the runtime/
\* attacker angle instead.
NoPrivilegeEscalation ==
  \A s \in SERVICES :
    \A o \in ReachableFromOriginal(s) :
      PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]

\*
\* INVARIANT 2: NoLateralMovement
\* A compromised service cannot grant itself access to a service it did not
\* originally have access to before it was compromised.
\*
\* Formal statement:
\*   If service a is compromised and adds a tuple <<a, rel, target>> that is
\*   not part of the original policy, target must already have been reachable
\*   from a under the ORIGINAL policy. (The attacker cannot extend their own
\*   reach through self-issued tuples.)
\*
\* Deliberately NOT "attacker-added tuple points above the attacker's own
\* level" — that version fires the instant ANY service is compromised in ANY
\* system with more than one privilege level (an attacker can always author a
\* bad-looking tuple), which is true regardless of whether the policy has a
\* real flaw. Checking against pre-compromise reachability is what actually
\* distinguishes "the attack succeeds" from "the attacker merely tried."
NoLateralMovement ==
  \A a \in compromised :
    \A t \in tuples :
      (t[1] = a /\ t \notin INITIAL_TUPLES) => t[3] \in ReachableFromOriginal(a)

---------------------------------------------------------------------------
\* LIVENESS (optional — not checked by default, requires fairness)
---------------------------------------------------------------------------

\* All legitimate authorization checks eventually succeed
\* (not checked in safety-only verification)
EventualConsistency ==
  []<>(\A s \in SERVICES : tuples /= {})

---------------------------------------------------------------------------
\* SPECIFICATION
---------------------------------------------------------------------------

Spec == Init /\ [][Next]_<<tuples, compromised>>

\* Properties to verify in TLC:
THEOREM Spec => [](TypeOK /\ NoPrivilegeEscalation /\ NoLateralMovement)

=============================================================================
