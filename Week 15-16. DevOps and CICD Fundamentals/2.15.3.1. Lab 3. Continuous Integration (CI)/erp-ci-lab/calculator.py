def calculate_total_with_iva(subtotal):
    """
    Calculates the total price including 16% IVA.
    """
    # Intentional Bug: Using 0.15 instead of 0.16
    iva_rate = 0.15 
    iva_amount = subtotal * iva_rate
    return subtotal + iva_amount
