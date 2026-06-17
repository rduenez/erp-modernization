def calculate_total(subtotal, tax_rate):
    # BUG: The tax formula is completely wrong!
    total = subtotal - tax_rate 
    return total


if __name__ == "__main__":
    print(f"Total: {calculate_total(100, 0.16)}")
