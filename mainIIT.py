# import sys
# import random
# from datetime import datetime

# from alpha_research import BacktesterIIT , Side, Ticker


# def my_broadcast_callback(state, ts):
#     # print(f"\n[STATIC] Timestamp: {ts}")
#     # for ticker, data in state.items():
#     #     print(f"{ticker}: {len(data)} timestamp={data['Time']} PRICE={data['Price']}")
#     # return
    

#     tickers = [t for t, d in state.items() if d['Price'] != 0]
#     buy_ticker = random.choice(tickers)
#     sell_ticker = random.choice([t for t in tickers if t != buy_ticker])
#     # place BUY
#     trade_buy = backtest.place_order(
#         ticker=buy_ticker,
#         qty=1,
#         side=Side.BUY
#     )
#     trade_sell = backtest.place_order(
#         ticker=sell_ticker,
#         qty=1,
#         side=Side.SELL
#     )


# def on_timer(ts):
#     print("On timer callback")


# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python main.py <config.json>")
#         sys.exit(1)

#     config_file = sys.argv[1]
#     backtest = BacktesterIIT(config_file)
#     print(datetime.now().strftime("%H:%M:%S"))  # only hh:mm:ss
#     backtest.run(broadcast_callback=my_broadcast_callback, timer_callback=on_timer)
#     print(datetime.now().strftime("%H:%M:%S"))  # only hh:mm:ss

import sys
from datetime import datetime
import pandas as pd

from alpha_research import BacktesterIIT, Side

# --- Global variables for SMA Strategy ---
price_history = []
short_window = 10   # fast moving average
long_window = 30    # slow moving average
current_position = None  # can be 'LONG', 'SHORT', or None


def my_broadcast_callback(state, ts):
    """
    Called every broadcast (tick update).
    Runs only for EBX ticker using SMA crossover strategy.
    """
    global price_history, current_position

    if "EBX" not in state:
        return

    data = state["EBX"]
    price = data["Price"]  # Use correct field name from your data dict
    if price == 0:
        return

    # Append price to history
    price_history.append(price)

    # Maintain only last 'long_window' prices
    if len(price_history) > long_window:
        price_history = price_history[-long_window:]

    # Wait until enough data for both SMAs
    if len(price_history) < long_window:
        return

    # Compute SMA short and long
    sma_short = pd.Series(price_history[-short_window:]).mean()
    sma_long = pd.Series(price_history).mean()

    # Generate Buy/Sell Signals
    if sma_short > sma_long and current_position != "LONG":
        backtest.place_order(ticker="EBX", qty=1, side=Side.BUY)
        current_position = "LONG"
        # print(f"[{ts}] BUY EBX @ {price:.2f} | SMA_short={sma_short:.2f}, SMA_long={sma_long:.2f}")

    elif sma_short < sma_long and current_position != "SHORT":
        backtest.place_order(ticker="EBX", qty=1, side=Side.SELL)
        current_position = "SHORT"
        # print(f"[{ts}] SELL EBX @ {price:.2f} | SMA_short={sma_short:.2f}, SMA_long={sma_long:.2f}")


def on_timer(ts):
    """Called every 'timer' seconds defined in configIIT.json"""
    # print(f"[{ts}] On timer callback")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        # print("Usage: python mainIIT.py <config.json>")
        sys.exit(1)

    config_file = sys.argv[1]
    backtest = BacktesterIIT(config_file)
    # print(datetime.now().strftime("%H:%M:%S"))  # Start time
    backtest.run(broadcast_callback=my_broadcast_callback, timer_callback=on_timer)
    # print(datetime.now().strftime("%H:%M:%S"))  # End time
