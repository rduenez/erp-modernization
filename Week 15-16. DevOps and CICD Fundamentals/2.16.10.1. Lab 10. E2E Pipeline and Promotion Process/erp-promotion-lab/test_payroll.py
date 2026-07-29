from payroll_api import calculate_isr

def test_isr_calculation():
    # 10,000 * 0.18 = 1800
    assert calculate_isr(10000) == 1800
