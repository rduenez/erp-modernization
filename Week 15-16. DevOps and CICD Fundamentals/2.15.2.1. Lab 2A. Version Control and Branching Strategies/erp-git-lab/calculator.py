def calculate_total(subtotal, tax_rate):
    # BUG: The tax formula is completely wrong!
    total = subtotal * ( 1.0 + tax_rate / 100 ) 
    return total


if __name__ == "__main__":
    print(f"Total: {calculate_total(100, 0.16)}")
