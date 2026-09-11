# FV-Zanzibar — actual TLC verification results

These are genuine, reproducible outputs from running TLC against
`Authorization.tla` + `Scenarios.tla`. They replace the previously-quoted
results table in the top-level README/thesis/paper draft, which had no
supporting `.cfg` file or evidence log anywhere in the repo and could not
have been produced from the spec as it was originally written (see "What
changed and why" below).

## How to reproduce

```bash
cd 03_prototype/tla_specs
java -jar ../../tools/tla2tools.jar -deadlock -config Baseline.cfg Scenarios.tla
java -jar ../../tools/tla2tools.jar -deadlock -config TransitiveLogging.cfg Scenarios.tla
java -jar ../../tools/tla2tools.jar -deadlock -config AdminCreep.cfg Scenarios.tla
```

`tla2tools.jar` is the official TLA+ tools release:
https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar

The `-deadlock` flag tells TLC to accept terminal states (e.g. once every
service has been compromised and nothing more can happen) instead of
reporting them as errors — expected for a small, finite attacker-action
model like this, not a spec bug.

## Results

| Scenario | Services | Invariant checked | TLC result | States explored | Wall time |
|---|---|---|---|---|---|
| `Baseline` | 3 | Both | **Pass** — no error found | 8 distinct | <1s |
| `TransitiveLogging` | 3 | `NoPrivilegeEscalation` | **FOUND**, at Init (static policy flaw) | 1 | <1s |
| `AdminCreep` | 3 | `NoLateralMovement` | **FOUND**, after compromise (runtime exploit) | 8 distinct | <1s |

Raw TLC output for each run is in this directory: `baseline_tlc_output.txt`,
`transitive_logging_tlc_output.txt`, `admin_creep_tlc_output.txt`.

Note the wall-clock times: these tiny (3-service) models check in well under
a second. The previously-quoted table (`8m 42s`–`13m 22s` per scenario) is
not plausible for a state space this size, and there is no larger/heavier
model checked in anywhere in this repo that would explain it.

## What changed in `Authorization.tla` and why

Actually running this (rather than treating it as done) surfaced four real
soundness problems in the spec as originally committed. Each is documented
inline at the relevant definition, summarized here:

1. **`ReachableFrom` was not transitive.** It only checked one-hop tuples, so
   the claimed "frontend reaches the sensitive DB through a shared logger"
   finding was structurally undetectable — that's a two-hop path. Fixed with
   a `RECURSIVE` closure that follows chains through intermediate services.

2. **`Next` let `AddTuple` fire for any subject/object pair, unconstrained.**
   This doesn't verify a *given* policy — it proves the tautology "if you
   allow arbitrary admin edits, arbitrary edits are possible," which is true
   of every predicate over every non-trivial permission hierarchy. Fixed by
   making the policy a fixed `INITIAL_TUPLES` constant (the thing Keto would
   actually have configured) and restricting `Next` to attacker moves only —
   this is what "verify a policy before deployment" has to mean.

3. **`NoPrivilegeEscalation` checked the live, attacker-mutable `tuples`,**
   so it failed the instant any service was compromised in any system with
   more than one privilege level — regardless of whether the *policy itself*
   had a flaw. Fixed to check against the static `INITIAL_TUPLES` graph
   (`ReachableFromOriginal`), which is what actually answers "is the
   deployed policy sound." The runtime/attacker question is `NoLateralMovement`'s job.

4. **`AttackerAddTuple` let a compromised service write literally any new
   tuple to literally any target.** That models "the attacker also has raw
   write access to Keto's admin API," which breaks every policy regardless
   of design — not a useful, policy-dependent result. Fixed to require the
   attacker already hold a `can_grant` relation over the target per the
   original policy (real Zanzibar semantics: `can_grant`/`owns` is what lets
   a subject manage another object's tuples). This is what makes `AdminCreep`
   a genuine, policy-specific finding rather than something that would have
   fired identically for every scenario.

There is also a base-case fix: `ReachableFrom`/`ReachableFromOriginal` now
include the subject itself (reflexive, zero-hop) — without it, a compromised
service adding a harmless self-loop tuple registered as a false-positive
"new access" finding (caught by actually running this against `Baseline` the
first time, before the `can_grant` gating fix existed).

## Scope, honestly

Three tiny, hand-built scenarios (3 services each) is a proof of concept
that the *mechanism* works and produces genuine, differentiated,
reproducible results — it is not yet the "4/5 buggy configurations" claim
from the original results table, and it does not yet demonstrate scaling
behavior (state space growth with service count) that a thesis chapter would
want to report. Next steps for a real evaluation: more scenarios matching
the originally-claimed bug classes ("wildcard over-grant", "circular trust"),
and a sweep over service count to characterize how TLC's runtime actually
scales — genuinely measured, not assumed.
