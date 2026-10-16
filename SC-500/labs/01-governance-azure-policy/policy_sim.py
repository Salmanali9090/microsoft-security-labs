"""Offline evaluator for a tiny subset of Azure Policy rule syntax (field/equals/notEquals/exists/allOf/anyOf/not).
Purpose: let a learner see WHY a resource is non-compliant without an Azure subscription.
It is a TEACHING SIMULATION - it does not replace Azure Policy evaluation."""
import json, pathlib

def _get(resource: dict, field: str):
    if field == "type":
        return resource.get("type")
    if field == "name":
        return resource.get("name")
    prop = field.split("/")[-1]
    return resource.get("properties", {}).get(prop, None)

def _missing(resource, field):
    return field.split("/")[-1] not in resource.get("properties", {}) and field not in ("type", "name")

def evaluate_condition(cond: dict, resource: dict) -> bool:
    if "allOf" in cond:
        return all(evaluate_condition(c, resource) for c in cond["allOf"])
    if "anyOf" in cond:
        return any(evaluate_condition(c, resource) for c in cond["anyOf"])
    if "not" in cond:
        return not evaluate_condition(cond["not"], resource)
    value = _get(resource, cond["field"])
    if "equals" in cond:
        return value == cond["equals"]
    if "notEquals" in cond:
        return value != cond["notEquals"]      # a missing property is not equal to the literal, so this is True
    if "exists" in cond:
        return (not _missing(resource, cond["field"])) == (str(cond["exists"]).lower() == "true")
    raise ValueError(f"unsupported condition: {cond}")

def evaluate_policy(policy_path, inventory, effect=None):
    policy = json.loads(pathlib.Path(policy_path).read_text())["properties"]
    effect = effect or policy["parameters"]["effect"]["defaultValue"]
    results = []
    for r in inventory:
        hit = evaluate_condition(policy["policyRule"]["if"], r)
        results.append({"name": r["name"], "compliant": not hit, "effect_if_noncompliant": effect if hit else None})
    return results

if __name__ == "__main__":
    here = pathlib.Path(__file__).resolve().parent
    inv = json.loads((here.parents[2] / "sample-data" / "resource_inventory.json").read_text())["resources"]
    for row in evaluate_policy(here / "policy_storage_public_access.json", inv):
        print(row)
