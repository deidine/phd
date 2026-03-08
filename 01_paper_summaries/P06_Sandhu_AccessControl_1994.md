# P06 — Sandhu & Samarati (1994). Access Control: Principles and Practice
**Venue:** IEEE Communications Magazine, 32(9), 40–48
**Date read:** Month 1, Week 4
**DOI:** https://doi.org/10.1109/35.312842
**Request PDF:** https://www.researchgate.net/publication/3404889

---

## Why I read this
Classic paper (~700 citations). Defines ACL, RBAC, MAC — vocabulary every
PhD student in security must know. Foundation for understanding why
ReBAC (Zanzibar) is an improvement.

---

## Access Control Matrix

The fundamental model: a matrix where rows are subjects (users, processes),
columns are objects (files, services, databases), and cells are permissions.

```
           | file:report | service:db | service:api |
-----------|-------------|------------|-------------|
user:alice |  read,write |            |    invoke   |
user:bob   |    read     |   query    |    invoke   |
svc:api    |             |   query    |             |
```

Problem: this matrix is enormous in real systems (millions of subjects × millions of objects).
Two practical representations:

- **ACL (Access Control List):** Store the matrix column-by-column. Each object carries a list of who can access it.
- **Capability list:** Store the matrix row-by-row. Each subject carries a list of what they can access.

---

## RBAC (Role-Based Access Control)

The key insight: most users in an organisation have the same permissions as others in the same job role. Instead of managing individual permissions, assign roles to users and permissions to roles.

```
user:deidine  →  role:phd_student  →  permissions: {read_papers, write_thesis, use_lab_computers}
user:supervisor →  role:professor  →  permissions: {read_papers, write_papers, grade_students, ...}
```

**Problem with RBAC for microservices:**
Roles are static. In microservices, permissions are contextual:
"Service A can call service B's /admin endpoint only if the request was initiated by a user with admin role and the request is part of a transaction tagged as privileged."
RBAC cannot express this contextual, chained, relationship-based condition.

---

## Why This Paper Matters for My Thesis

This paper is cited in Chapter 2, Section 2.2 (Access Control Models) to:
1. Define the foundational vocabulary (ACL, RBAC, MAC)
2. Show the evolution from simple to complex models
3. Motivate why Zanzibar/ReBAC (Pang et al., 2019) is needed for distributed microservices

The progression I use in Chapter 2:
```
ACL → RBAC → ReBAC (Zanzibar)
(1970s)  (1992)  (2019)
```
Each step solves the limitations of the previous. My thesis builds on ReBAC.
