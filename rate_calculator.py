def calculate_rate(amount, period):
    if period == 0:
        return 0.0
    return float(round(amount / period))

if __name__ == "__main__":
    print(calculate_rate(100, 0))
