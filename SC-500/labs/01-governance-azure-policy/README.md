# Lab 01 – Governance with Azure Policy (policy-as-code)

**Goal:** understand how Azure Policy turns a security rule into an automatic *audit* or *deny* control, and read a policy definition like an engineer.
**Docs:** [Azure Policy overview](https://learn.microsoft.com/azure/governance/policy/overview) · [Defender for Cloud introduction](https://learn.microsoft.com/azure/defender-for-cloud/defender-for-cloud-introduction)

## Concepts
- A **policy definition** = rule (`if` conditions → `then` effect). A **policy assignment** applies a definition to a scope (management group, subscription, resource group).
- **Effects** used here: `Audit` (report only) and `Deny` (block creation/update). Start with **Audit**, review impact, then consider **Deny**.
- A **custom** definition is for gaps; check built-in definitions first – they are maintained by Microsoft.

## Files
- [`policy_storage_public_access.json`](policy_storage_public_access.json) – flags storage accounts whose `allowBlobPublicAccess` is not explicitly `false`.
- [`policy_sim.py`](policy_sim.py) – offline evaluator for a small subset of policy syntax.

## Part A – offline (10 minutes)
```bash
python SC-500/labs/01-governance-azure-policy/policy_sim.py
```
**Expected output** (synthetic inventory):
| Resource | Compliant? | Why |
|---|---|---|
| `stlabcompliant01` | yes | `allowBlobPublicAccess: false` |
| `stlabpublic02` | **no** | `allowBlobPublicAccess: true` |
| `stlabdefault03` | **no** | property absent → "not explicitly false" → flagged |
| `kvlab01` | yes | not a storage account, rule does not apply |

Exercises: (1) change the rule so only `true` is flagged – what risk does that reintroduce? (2) run with `effect="Deny"` in a test and explain what changes for *existing* resources vs *new* ones.

## Part B – in a lab subscription (⚠️ untested by the author)
1. In the Azure portal open **Policy → Definitions → + Policy definition** and create the definition from the JSON (the portal separates rule and parameter fields; consult the docs for the current layout, or deploy with Bicep/CLI/REST).
2. Assign it to a **lab resource group** with effect `Audit`.
3. Wait for evaluation, then open **Policy → Compliance** to see non-compliant resources.
4. Only after reviewing impact, test `Deny` on the lab resource group.
5. Clean up the assignment and definition.

## Limitations
The simulator supports only `field/equals/notEquals/exists/allOf/anyOf/not`; real Azure Policy has aliases, modes, `deployIfNotExists`, exemptions and more. The custom policy is a teaching example, not a replacement for built-in policies.
