from calculator import calculate_total_with_iva

def test_calculate_total_with_iva():
    # If the subtotal is 100, a 16% IVA means the total should be 116.
    result = calculate_total_with_iva(100.00)
    assert result == 116.00, f"Expected 116.00, but got {result}"
