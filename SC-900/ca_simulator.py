"""Conditional Access - SIMPLIFIED TEACHING MODEL.

This is NOT Microsoft's policy engine. It only illustrates the idea
"signals -> decision -> enforcement" so a beginner can reason about it.
It ignores report-only mode, session controls, authentication strengths, device filters,
and many other real features. See the official docs linked in SC-900/README.md.
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SignIn:
    user: str
    groups: list = field(default_factory=list)
    app: str = "Office 365"
    country: str = "PK"
    sign_in_risk: str = "none"        # none | low | medium | high
    device_compliant: bool = False
    mfa_completed: bool = False

def _applies(policy: dict, s: SignIn) -> bool:
    c = policy["conditions"]
    users = c.get("includeGroups")
    if users and not set(users) & set(s.groups):
        return False
    if s.user in c.get("excludeUsers", []):
        return False
    apps = c.get("includeApps")
    if apps and s.app not in apps and "All" not in apps:
        return False
    risks = c.get("signInRiskLevels")
    if risks and s.sign_in_risk not in risks:
        return False
    blocked = c.get("includeCountries")
    if blocked and s.country not in blocked:
        return False
    return True

def evaluate(policies: list, s: SignIn) -> dict:
    """Returns {'decision': 'allow'|'block'|'grant_with_controls', 'unmet': [...], 'matched': [...]}.
    Teaching rules: any matching Block policy wins; otherwise every matching policy's controls must all be satisfied."""
    matched = [p for p in policies if p.get("state", "enabled") == "enabled" and _applies(p, s)]
    if any(p["grant"].get("block") for p in matched):
        return {"decision": "block", "unmet": [], "matched": [p["name"] for p in matched]}
    unmet = []
    for p in matched:
        g = p["grant"]
        if g.get("requireMfa") and not s.mfa_completed:
            unmet.append("mfa")
        if g.get("requireCompliantDevice") and not s.device_compliant:
            unmet.append("compliant_device")
    unmet = sorted(set(unmet))
    if not matched:
        return {"decision": "allow", "unmet": [], "matched": []}
    return {"decision": "grant_with_controls" if unmet else "allow", "unmet": unmet, "matched": [p["name"] for p in matched]}

EXAMPLE_POLICIES = [
    {"name": "Require MFA for admins", "state": "enabled",
     "conditions": {"includeGroups": ["Admins"], "includeApps": ["All"]}, "grant": {"requireMfa": True}},
    {"name": "Block high-risk sign-ins", "state": "enabled",
     "conditions": {"includeApps": ["All"], "signInRiskLevels": ["high"]}, "grant": {"block": True}},
    {"name": "Require compliant device for Finance app", "state": "enabled",
     "conditions": {"includeApps": ["Finance Portal"]}, "grant": {"requireCompliantDevice": True}},
]

if __name__ == "__main__":
    demo = SignIn(user="alice@contoso.example", groups=["Admins"], app="Finance Portal")
    print(evaluate(EXAMPLE_POLICIES, demo))
