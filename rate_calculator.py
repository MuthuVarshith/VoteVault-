def calculate_rate(amount, period):
    return amount / period  # BUG: no zero-division guard

if __name__ == "__main__":
    print(calculate_rate(100, 0))
