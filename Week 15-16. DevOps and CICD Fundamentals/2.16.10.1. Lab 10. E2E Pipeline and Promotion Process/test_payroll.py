from payroll_api import calculate_isr

def test_isr_calculation():
    # 10,000 * 0.20 = 2000
    assert calculate_isr(10000) == 2000
