from app.core.rate_limit import SlidingWindowGate


def test_gate_rejects_after_limit() -> None:
    gate = SlidingWindowGate(max_entries=4, requests=2, window_seconds=60)
    assert gate.allow(10)
    assert gate.allow(10)
    assert not gate.allow(10)
