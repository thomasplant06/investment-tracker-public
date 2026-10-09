import pandas as pd, numpy as np, yfinance as yf

TICKER = "V40A.AS"       # Vanguard LifeStrategy 40% Acc, euro listing
CASH_RATE = 0.04         # set this to your cash ISA's AER
GBP_CASH = 500           # your cash buffer, in pounds
EURGBP = 1.18013317      # same rate as your trades, so cash is in euros too

trades = pd.read_csv("trades.csv")
units = trades["units"].sum()
cost = trades["total"].sum()                 # euros
start = pd.to_datetime(trades["date"].min()).strftime("%Y-%m-%d")

px = yf.Ticker(TICKER).history(start=start, auto_adjust=True)["Close"]
px.index = px.index.tz_localize(None)

value = units * px
returns = px.pct_change().dropna()
drawdown = value / value.cummax() - 1

days = np.array((px.index - px.index[0]).days)
cash_start = GBP_CASH * EURGBP
cash = pd.Series(cash_start * (1 + CASH_RATE) ** (days / 365), index=px.index)

summary = {
    "cost_eur": round(cost, 2),
    "latest_value_eur": round(value.iloc[-1], 2),
    "fund_return_%": round(100 * (value.iloc[-1] / cost - 1), 2),
    "cash_return_%": round(100 * (cash.iloc[-1] / cash_start - 1), 2),
    "annualised_vol_%": round(100 * returns.std() * np.sqrt(252), 2),
    "max_drawdown_%": round(100 * drawdown.min(), 2),
}
print(pd.Series(summary))

pd.DataFrame({"fund_value": value, "cash_value": cash, "drawdown": drawdown}).to_csv("tracker.csv")
