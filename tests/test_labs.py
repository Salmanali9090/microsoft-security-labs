import json, pathlib
import ca_simulator as ca
import policy_sim as ps

ROOT = pathlib.Path(__file__).resolve().parents[1]

def test_ca_block_wins_over_other_controls():
    s = ca.SignIn("a@contoso.example", groups=["Admins"], sign_in_risk="high", mfa_completed=True)
    assert ca.evaluate(ca.EXAMPLE_POLICIES, s)["decision"] == "block"

def test_ca_requires_mfa_for_admins_then_allows_after_mfa():
    s = ca.SignIn("a@contoso.example", groups=["Admins"])
    assert ca.evaluate(ca.EXAMPLE_POLICIES, s) == {"decision": "grant_with_controls", "unmet": ["mfa"], "matched": ["Require MFA for admins"]}
    s.mfa_completed = True
    assert ca.evaluate(ca.EXAMPLE_POLICIES, s)["decision"] == "allow"

def test_ca_no_matching_policy_allows():
    assert ca.evaluate(ca.EXAMPLE_POLICIES, ca.SignIn("x@contoso.example"))["decision"] == "allow"

def test_ca_excluded_user_skipped():
    pol = [{"name": "p", "conditions": {"includeApps": ["All"], "excludeUsers": ["breakglass@contoso.example"]}, "grant": {"requireMfa": True}}]
    assert ca.evaluate(pol, ca.SignIn("breakglass@contoso.example"))["decision"] == "allow"

def test_policy_json_is_valid_and_has_required_shape():
    p = json.loads((ROOT / "SC-500/labs/01-governance-azure-policy/policy_storage_public_access.json").read_text())["properties"]
    assert p["policyType"] == "Custom" and p["mode"] == "Indexed"
    assert p["parameters"]["effect"]["defaultValue"] in p["parameters"]["effect"]["allowedValues"]
    assert "if" in p["policyRule"] and "then" in p["policyRule"]

def test_policy_simulation_flags_public_and_default_accounts():
    inv = json.loads((ROOT / "sample-data/resource_inventory.json").read_text())["resources"]
    res = {r["name"]: r["compliant"] for r in ps.evaluate_policy(
        ROOT / "SC-500/labs/01-governance-azure-policy/policy_storage_public_access.json", inv)}
    assert res == {"stlabcompliant01": True, "stlabpublic02": False, "stlabdefault03": False, "kvlab01": True}

def test_policy_effect_parameter_can_be_overridden():
    inv = [{"name": "x", "type": "Microsoft.Storage/storageAccounts", "properties": {"allowBlobPublicAccess": True}}]
    out = ps.evaluate_policy(ROOT / "SC-500/labs/01-governance-azure-policy/policy_storage_public_access.json", inv, effect="Deny")
    assert out[0]["effect_if_noncompliant"] == "Deny"
