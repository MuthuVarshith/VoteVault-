def calculate_rate(amount, period):
    try:
        return amount / period
    except ZeroDivisionError:
        return None

if __name__ == "__main__":
    print(calculate_rate(100, 0))
