from scripts.verify_parity import verify


def test_original_logic_inventory_is_preserved() -> None:
    result = verify()
    assert result["ok"], result["failures"]
    assert result["totals"]["sources"] == 67
    assert result["totals"]["source_classes"] <= result["totals"]["destination_classes"]
    assert result["totals"]["source_functions"] == result["totals"]["destination_functions"]
    assert result["totals"]["source_decorated_functions"] == result["totals"]["destination_decorated_functions"]
    assert result["totals"]["source_decorator_entries"] == result["totals"]["destination_decorator_entries"]
