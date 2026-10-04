from src.digest_service import SaaSRecord, select_attention


def test_attention_queue_keeps_high_priority_lifecycle_events():
    records = [
        SaaSRecord("t1", "a1", "tenant onboarding review", "urgent"),
        SaaSRecord("t1", "a2", "account active", "low"),
        SaaSRecord("t2", "a3", "admin access change", "high"),
    ]
    kept = select_attention(records)
    assert [(item.account, item.priority) for item in kept] == [("a1", "urgent"), ("a3", "high")]
