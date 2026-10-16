# Lab 03 – Identity and privileged access

**Goal:** reduce the blast radius of a compromised identity (the story from the [SC-200 lab](../../../SC-200/README.md)).
**Docs:** [Privileged Identity Management](https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure) · [Managed identities](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) · [Conditional Access](https://learn.microsoft.com/entra/identity/conditional-access/overview)

## Principles
1. **Least privilege** – grant the smallest role at the smallest scope.
2. **Just-in-time** – make admin roles *eligible* (time-bound activation with justification/approval/MFA) instead of permanently active; this is what Microsoft Entra PIM provides (feature licensing applies – check docs).
3. **No stored secrets** – workloads authenticate with **managed identities**; secrets that remain live in **Azure Key Vault** with RBAC authorization.
4. **Separate roles** – Entra directory roles (e.g. Global Administrator) vs Azure RBAC roles (e.g. Contributor) are different systems; review both.
5. **Watch privileged changes** – alert on role assignments (see detections [03](../../../detections/03_privileged_role_assignment.kql) and [05](../../../detections/05_azure_rbac_assignment_unapproved.kql)).

## Hardening checklist (tick in your lab)
- [ ] Two emergency (break-glass) accounts: cloud-only, excluded from Conditional Access policies, protected with strong credentials, and covered by an alert on every sign-in.
- [ ] Admin roles are *eligible* via PIM, not permanent; activation requires MFA.
- [ ] Conditional Access requires phishing-resistant MFA for admins ([SC-900 simulator](../../../SC-900/README.md)).
- [ ] No Owner/Contributor assigned to individual users at subscription scope without justification; review with `az role assignment list --all` (⚠️ untested).
- [ ] App/service access uses managed identity: `az identity create -g <rg> -n <name>` (⚠️ untested).
- [ ] Key Vault uses RBAC authorization and soft delete/purge protection.
- [ ] Alerts for role-assignment writes and key regeneration are enabled and tested.

## Exercise
Using the synthetic incident: which two controls above would most limit what `alice` could do at 09:35 and 09:50? *(Suggested: PIM-eligible roles for admin rights, and Conditional Access / phishing-resistant MFA so the guessed password alone is not enough.)*

## Status
📚 Conceptual lab. The only executable parts are the simulated detections 03 and 05.
