import csv
from datetime import datetime

STOCK_PRICES = {
    "AAPL": 500,    # Apple Inc.
    "MSFT": 113,   # Microsoft Corporation
    "GOOGL": 380,   # Alphabet Inc. (Google)
    "AMZN": 400,    # Amazon.com Inc.
    "TSLA": 690,    # Tesla Inc.
    "META": 130,   # Meta Platforms Inc.
    "NFLX": 140,   # Netflix Inc.
    "NVDA": 360,    # NVIDIA Corporation
    "JPM": 650,     # JPMorgan Chase & Co.
    "V": 750,       # Visa Inc.
    "WMT": 220,     # Walmart Inc.
    "DIS": 380,     # The Walt Disney Company
    "KO": 180,      # The Coca-Cola Company
    "MCD": 840,     # McDonald's Corporation
    "NKE": 240,     # Nike Inc.
    "SBUX": 260,    # Starbucks Corporation
    "ADBE": 160,   # Adobe Inc.
    "INTC": 620,      # Intel Corporation
    "PYPL": 190,    # PayPal Holdings Inc.
    "UBER": 180     # Uber Technologies Inc.
}

def display_available_stocks():

    print("  Available stocks (price per share in PKR):")
    print("  " + "-" * 34)
    for symbol, price in STOCK_PRICES.items():
        print("  " + symbol.ljust(8) + "Rs. " + format(price, ","))
    print("  " + "-" * 34)

def get_stock_symbol():
    while True:
        symbol = input("  Enter stock symbol (or DONE to finish): ").strip().upper()

        if symbol == "DONE":
            return None

        if symbol not in STOCK_PRICES:
            print("  '" + symbol + "' is not in the stock list. Please choose from the list above.")
            continue

        return symbol

def get_quantity(symbol):
    while True:
        quantity_input = input("  Enter quantity of " + symbol + " shares: ").strip()

        if not quantity_input.isdigit():
            print("  Please enter a valid whole number.")
            continue

        quantity = int(quantity_input)

        if quantity <= 0:
            print("  Quantity must be greater than zero.")
            continue

        return quantity

def build_portfolio():
    portfolio = {}

    while True:
        symbol = get_stock_symbol()

        if symbol is None:
            break

        quantity = get_quantity(symbol)

        if symbol in portfolio:
            portfolio[symbol] += quantity
        else:
            portfolio[symbol] = quantity

        print("  Added " + str(quantity) + " share(s) of " + symbol + " to your portfolio.")
        print()

    return portfolio

def calculate_summary(portfolio):
    summary = []
    total_investment = 0

    for symbol, quantity in portfolio.items():
        price = STOCK_PRICES[symbol]
        value = price * quantity
        total_investment += value
        summary.append({
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "value": value
        })

    return summary, total_investment

def display_summary(summary, total_investment):
    print()
    print("=" * 58)
    print("                  PORTFOLIO SUMMARY")
    print("=" * 58)
    print("  " + "Stock".ljust(8) + "Qty".ljust(8) + "Price (PKR)".ljust(16) + "Value (PKR)")
    print("  " + "-" * 52)

    for entry in summary:
        print(
            "  " +
            entry["symbol"].ljust(8) +
            str(entry["quantity"]).ljust(8) +
            ("Rs. " + format(entry["price"], ",")).ljust(16) +
            "Rs. " + format(entry["value"], ",")
        )

    print("  " + "-" * 52)
    print("  Total investment value : Rs. " + format(total_investment, ","))
    print("=" * 58)

def save_to_csv(summary, total_investment):
    filename = "portfolio_summary.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Generated on", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Currency", "PKR"])
        writer.writerow([])
        writer.writerow(["Stock", "Quantity", "Price Per Share (PKR)", "Total Value (PKR)"])

        for entry in summary:
            writer.writerow([entry["symbol"], entry["quantity"], entry["price"], entry["value"]])

        writer.writerow([])
        writer.writerow(["Total Investment", "", "", total_investment])

    print("  Portfolio saved to " + filename)
    print()

def run_tracker():
    print()
    print("=" * 58)
    print("           STOCK PORTFOLIO TRACKER (PKR)")
    print("=" * 58)
    print("  Build your portfolio by entering stocks you own.")
    print("  All prices are shown in Pakistani Rupees (PKR).")

    display_available_stocks()

    portfolio = build_portfolio()

    if not portfolio:
        print("  No stocks were added. Exiting.")
        print()
        return

    summary, total_investment = calculate_summary(portfolio)
    display_summary(summary, total_investment)

    save_choice = input("  Save this summary to a CSV file? (yes / no): ").strip().lower()

    if save_choice in ("yes", "y"):
        save_to_csv(summary, total_investment)
    else:
        print("  Summary was not saved.")

    print("  Thank you for using the Stock Portfolio Tracker.")

run_tracker()
