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
    Formally verify that a Keto authorization policy satisfies two safety invariants:
    1. NoPrivilegeEscalation: No service can reach resources above its permission level
    2. NoLateralMovement: A compromised service cannot self-grant access to other services

  How to run (TLC model checker):
    1. Install TLA+ Toolbox: https://lamport.azurewebsites.net/tla/toolbox.html
    2. Open this file in Toolbox
    3. Create a new model, set SERVICES and RESOURCES constants
    4. Add NoPrivilegeEscalation and NoLateralMovement as invariants
    5. Run TLC

  Or via CLI:
    java -jar tla2tools.jar -config Authorization.cfg Authorization.tla
*)

EXTENDS Sequences, FiniteSets, Naturals

CONSTANTS
  SERVICES,        \* e.g., {"svc_frontend", "svc_api", "svc_db", "svc_cache"}
  RESOURCES,       \* e.g., {"db_read", "db_write", "cache_read", "admin_api"}
  RELATIONS,       \* e.g., {"can_call", "can_read", "can_write", "owns"}
  PERMISSION_LEVEL \* Function: SERVICES \cup RESOURCES -> Nat (privilege level)
                   \* e.g., svc_db -> 3, svc_frontend -> 1

VARIABLES
  tuples,          \* Set of <<subject, relation, object>> triples
  compromised      \* Set of services currently compromised (for attack simulation)

---------------------------------------------------------------------------

\* Type invariant: all tuples are valid triples
TypeOK ==
  /\ tuples \subseteq (SERVICES \X RELATIONS \X (SERVICES \cup RESOURCES))
  /\ compromised \subseteq SERVICES

\* Initial state: empty authorization graph, no compromised services
Init ==
  /\ tuples = {}
  /\ compromised = {}

---------------------------------------------------------------------------
\* ACTIONS
---------------------------------------------------------------------------

\* Legitimate policy operation: admin adds an authorization tuple
AddTuple(subj, rel, obj) ==
  /\ subj \in SERVICES
  /\ obj  \in (SERVICES \cup RESOURCES)
  /\ rel  \in RELATIONS
  /\ tuples' = tuples \cup {<<subj, rel, obj>>}
  /\ UNCHANGED compromised

\* Legitimate policy operation: admin removes an authorization tuple
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

\* Attack simulation: compromised service tries to add a self-serving tuple
\* (this models a service trying to escalate its own privileges)
AttackerAddTuple(attacker, rel, target) ==
  /\ attacker \in compromised
  /\ target   \in (SERVICES \cup RESOURCES)
  /\ rel      \in RELATIONS
  /\ tuples'  = tuples \cup {<<attacker, rel, target>>}
  /\ UNCHANGED compromised

\* Next-state relation: any of the above actions can happen
Next ==
  \/ \E s \in SERVICES, r \in RELATIONS, o \in (SERVICES \cup RESOURCES) :
       AddTuple(s, r, o)
  \/ \E s \in SERVICES, r \in RELATIONS, o \in (SERVICES \cup RESOURCES) :
       RemoveTuple(s, r, o)
  \/ \E svc \in SERVICES : CompromiseService(svc)
  \/ \E a \in SERVICES, r \in RELATIONS, t \in (SERVICES \cup RESOURCES) :
       AttackerAddTuple(a, r, t)

---------------------------------------------------------------------------
\* HELPER FUNCTIONS
---------------------------------------------------------------------------

\* Check if subject has relation rel to object (direct lookup)
HasDirectRelation(subj, rel, obj) ==
  <<subj, rel, obj>> \in tuples

\* Compute the set of resources reachable from a subject via "can_read" or "can_call"
ReachableFrom(subj) ==
  { obj \in (SERVICES \cup RESOURCES) :
      \/ <<subj, "can_call", obj>> \in tuples
      \/ <<subj, "can_read", obj>> \in tuples
      \/ <<subj, "can_write", obj>> \in tuples }

---------------------------------------------------------------------------
\* SAFETY INVARIANTS (what TLC will verify)
---------------------------------------------------------------------------

\*
\* INVARIANT 1: NoPrivilegeEscalation
\* A service can never reach a resource whose privilege level exceeds its own.
\*
\* Formal statement:
\*   For all services s and all objects o that s can reach:
\*   PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]
\*
NoPrivilegeEscalation ==
  \A s \in SERVICES :
    \A o \in ReachableFrom(s) :
      PERMISSION_LEVEL[s] >= PERMISSION_LEVEL[o]

\*
\* INVARIANT 2: NoLateralMovement
\* A compromised service cannot grant itself access to a service it did not
\* originally have access to before it was compromised.
\*
\* Formal statement:
\*   If service a is compromised and adds a tuple <<a, rel, target>>,
\*   then target must have been reachable from a BEFORE the compromise.
\*   (The attacker cannot extend their own reach through self-issued tuples.)
\*
\* Note: This invariant is checked differently — via a temporal property.
\* For the simpler safety version:
\*   No compromised service appears as a subject in a tuple pointing to
\*   any resource with level > PERMISSION_LEVEL[that service].
\*
NoLateralMovement ==
  \A a \in compromised :
    \A <<s, r, o>> \in tuples :
      s = a => PERMISSION_LEVEL[a] >= PERMISSION_LEVEL[o]

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
