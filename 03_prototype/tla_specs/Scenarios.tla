---------------------------------- MODULE Scenarios ----------------------------------
(*
  Concrete constant instantiations for Authorization.tla. Each Scenario_*
  operator group fixes SERVICES/RESOURCES/RELATIONS/PERMISSION_LEVEL/
  INITIAL_TUPLES for one policy under test; a matching .cfg file in this
  directory selects one group via CONSTANT ... <- overrides.

  All identifiers below are plain TLA+ strings (not TLC "model values") so
  they can be written as ordinary literals here with no extra CONSTANTS
  bookkeeping — PERMISSION_LEVEL is a TLA+ record literal, which is exactly
  a function whose domain is the set of its field-name strings, so
  PERMISSION_LEVEL["svc_frontend"] and PERMISSION_LEVEL.svc_frontend are the
  same lookup.
*)
EXTENDS Authorization

\* ============================================================================
\* Baseline — a level-consistent policy: nothing at level 1 has any path,
\* direct or transitive, to anything above level 1. Both invariants should
\* hold throughout (Init and after any attacker action).
\* ============================================================================
Baseline_SERVICES  == {"svc_frontend", "svc_api", "svc_db"}
Baseline_RESOURCES == {"public_cache", "db_sensitive"}
Baseline_RELATIONS == {"can_call", "can_read", "can_write", "can_grant"}
Baseline_PERMISSION_LEVEL ==
  [svc_frontend |-> 1, svc_api |-> 1, svc_db |-> 3,
   public_cache |-> 1, db_sensitive |-> 3]
Baseline_INITIAL_TUPLES ==
  { <<"svc_frontend", "can_call", "svc_api">>,
    <<"svc_api", "can_read", "public_cache">>,
    <<"svc_db", "can_write", "db_sensitive">> }

\* ============================================================================
\* TransitiveLogging — the flagship claimed bug. svc_frontend (level 1) has
\* no DIRECT tuple to db_sensitive (level 3), but reaches it in two hops
\* through svc_logger (level 1) — a service under-leveled because "it's just
\* a logger," while still legitimately needing write access to the sensitive
\* DB for audit purposes. A reviewer checking each edge in isolation
\* (frontend->logger looks fine; logger->db looks fine, since logger *does*
\* need that access) would not see the transitive implication.
\* ============================================================================
TL_SERVICES  == {"svc_frontend", "svc_api", "svc_logger"}
TL_RESOURCES == {"db_sensitive"}
TL_RELATIONS == {"can_call", "can_read", "can_write", "can_grant"}
TL_PERMISSION_LEVEL ==
  [svc_frontend |-> 1, svc_api |-> 2, svc_logger |-> 1, db_sensitive |-> 3]
TL_INITIAL_TUPLES ==
  { <<"svc_frontend", "can_call", "svc_logger">>,
    <<"svc_logger", "can_write", "db_sensitive">> }

\* ============================================================================
\* AdminCreep — the policy graph itself is level-consistent (same shape as
\* Baseline: no static NoPrivilegeEscalation violation), but svc_logger was
\* additionally granted "can_grant" over db_sensitive at some point — e.g. an
\* engineer needed to let the logging service rotate/administer a specific
\* Keto tuple during an incident and the grant was never revoked ("creep").
\* Compromising svc_logger should then let AttackerAddTuple hand it NEW
\* direct access to db_sensitive it never had via can_call/can_read/
\* can_write — genuine, policy-dependent lateral movement, not a modeling
\* artifact of an unconstrained attacker.
\* ============================================================================
AC_SERVICES  == {"svc_frontend", "svc_logger", "svc_db"}
AC_RESOURCES == {"db_sensitive"}
AC_RELATIONS == {"can_call", "can_read", "can_write", "can_grant"}
AC_PERMISSION_LEVEL ==
  [svc_frontend |-> 1, svc_logger |-> 1, svc_db |-> 3, db_sensitive |-> 3]
AC_INITIAL_TUPLES ==
  { <<"svc_frontend", "can_call", "svc_logger">>,
    <<"svc_db", "can_write", "db_sensitive">>,
    <<"svc_logger", "can_grant", "db_sensitive">> }

========================================================================================
