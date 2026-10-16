from datetime import datetime
import detection_logic as d

ATT = "203.0.113.10"

def test_password_spray_finds_only_the_attacker_bin():
    assert d.password_spray(d.signin()) == [(ATT, datetime(2026, 1, 10, 8, 0), 16, 12)]

def test_success_after_failures_finds_alice_only():
    hits = d.success_after_failures(d.signin())
    assert hits == [("alice@contoso.example", ATT, 6, datetime(2026, 1, 10, 9, 15), datetime(2026, 1, 10, 9, 20))]

def test_benign_mistyped_password_is_not_flagged():
    assert all(h[0] != "bob@contoso.example" for h in d.success_after_failures(d.signin()))

def test_privileged_role_assignment_returns_two_rows_for_review():
    rows = d.privileged_role_assignment(d.audit())
    assert [(r[1], r[3]) for r in rows] == [("it.admin@contoso.example", "Security Administrator"),
                                           ("alice@contoso.example", "Global Administrator")]

def test_non_privileged_role_and_other_operations_ignored():
    roles = {r[3] for r in d.privileged_role_assignment(d.audit())}
    assert "Helpdesk Administrator" not in roles

def test_encoded_powershell_one_hit():
    assert d.encoded_powershell(d.device()) == [("2026-01-10T09:42:00Z", "SYN-WKS-014", "alice")]

def test_encoded_regex_negative_and_positive_cases():
    assert d.PS_RE.search("powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQA")
    assert d.PS_RE.search("pwsh.exe -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQA")
    assert not d.PS_RE.search("powershell.exe -File backup.ps1")
    assert not d.PS_RE.search("powershell.exe -e abc")

def test_rbac_unapproved_caller_only_alice():
    assert d.rbac_unapproved(d.activity()) == [("2026-01-10T09:50:00Z", "alice@contoso.example", ATT)]

def test_ai_key_regeneration_only_alice():
    assert d.ai_key_regen(d.activity()) == [("2026-01-10T09:55:00Z", "alice@contoso.example", ATT)]
