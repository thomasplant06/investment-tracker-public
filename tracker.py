import pandas as pd, numpy as np, yfinance as yf
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font

TICKER = "V40A.AS"        # Vanguard LifeStrategy 40% Acc, euro listing
FX_TICKER = "EURGBP=X"    # pounds per 1 euro, from Yahoo Finance
CASH_RATE = 0.04          # set this to your cash ISA's AER
GBP_CASH = 500            # your cash buffer, in pounds
TRADE_EUR_PER_GBP = 1.18013317   # the rate you got when you bought

# ---------- 1. Load trades and download market data ----------
trades = pd.read_csv("trades.csv")
units = trades["units"].sum()
cost_eur = trades["total"].sum()
cost_gbp = cost_eur / TRADE_EUR_PER_GBP
start = pd.to_datetime(trades["date"].min()).strftime("%Y-%m-%d")

def close(ticker):
    s = yf.Ticker(ticker).history(start=start, auto_adjust=True)["Close"]
    s.index = s.index.tz_localize(None).normalize()
    return s

px = close(TICKER)                                  # fund price, euros
fx = close(FX_TICKER).reindex(px.index).ffill().bfill()   # pounds per euro

# ---------- 2. Calculations (all in pounds unless named _eur) ----------
value_eur = units * px
value_gbp = value_eur * fx
days = np.array((px.index - px.index[0]).days)
cash_gbp = pd.Series(GBP_CASH * (1 + CASH_RATE) ** (days / 365), index=px.index)
daily_ret = value_gbp.pct_change().dropna()
drawdown = value_gbp / value_gbp.cummax() - 1

fund_ret_eur = value_eur.iloc[-1] / cost_eur - 1          # what the fund did
fx_ret = fx.iloc[-1] * TRADE_EUR_PER_GBP - 1              # what the euro did vs the pound
total_ret_gbp = value_gbp.iloc[-1] / cost_gbp - 1         # what you actually made
cash_ret = cash_gbp.iloc[-1] / GBP_CASH - 1

summary = {
    "cost_gbp": round(cost_gbp, 2),
    "latest_value_gbp": round(value_gbp.iloc[-1], 2),
    "fund_return_eur_%": round(100 * fund_ret_eur, 2),
    "currency_effect_%": round(100 * fx_ret, 2),
    "total_return_gbp_%": round(100 * total_ret_gbp, 2),
    "cash_return_%": round(100 * cash_ret, 2),
    "annualised_vol_%": round(100 * daily_ret.std() * np.sqrt(252), 2),
    "max_drawdown_%": round(100 * drawdown.min(), 2),
}
print(pd.Series(summary))

pd.DataFrame({"fund_value_gbp": value_gbp, "cash_value_gbp": cash_gbp,
              "drawdown": drawdown}).to_csv("tracker.csv")

# ---------- 3. Excel workbook with live formulas ----------
wb = Workbook()
bold, blue = Font(bold=True), Font(color="0000FF")   # blue = an input you can change

# Trades sheet: a copy of trades.csv
ws_t = wb.active
ws_t.title = "Trades"
ws_t.append(list(trades.columns))
for row in trades.itertuples(index=False):
    ws_t.append(list(row))

# Summary sheet: inputs at the top, results underneath
ws_s = wb.create_sheet("Summary")
n = len(px) + 1                                      # last data row on Prices
rows = [
    ("INPUTS", None, None),
    ("Cash rate (AER)", CASH_RATE, "0.00%"),
    ("Cash benchmark (£)", GBP_CASH, "£#,##0.00"),
    ("EUR per GBP at purchase", TRADE_EUR_PER_GBP, "0.0000"),
    (None, None, None),
    ("HOLDING", None, None),
    ("Units held", "=SUM(Trades!C:C)", "0.0000"),
    ("Cost (€, incl. fees)", "=SUM(Trades!F:F)", "€#,##0.00"),
    ("Cost (£)", "=B8/B4", "£#,##0.00"),
    ("Latest value (€)", f"=Prices!D{n}", "€#,##0.00"),
    ("Latest value (£)", f"=Prices!E{n}", "£#,##0.00"),
    (None, None, None),
    ("PERFORMANCE", None, None),
    ("Fund return in euros", "=B10/B8-1", "0.00%"),
    ("Currency effect (EUR vs GBP)", f"=Prices!C{n}*B4-1", "0.00%"),
    ("Total return in pounds", "=B11/B9-1", "0.00%"),
    ("Cash benchmark return", f"=Prices!F{n}/B3-1", "0.00%"),
    ("Fund minus cash", "=B16-B17", "0.00%"),
    (None, None, None),
    ("RISK", None, None),
    ("Annualised volatility", f"=STDEV(Prices!G3:G{n})*SQRT(252)", "0.00%"),
    ("Maximum drawdown", f"=MIN(Prices!H2:H{n})", "0.00%"),
]
for r, (label, val, fmt) in enumerate(rows, start=1):
    ws_s.cell(r, 1, label)
    if val is None:
        ws_s.cell(r, 1).font = bold
    else:
        c = ws_s.cell(r, 2, val)
        c.number_format = fmt
        if r <= 4:
            c.font = blue
ws_s.column_dimensions["A"].width = 30
ws_s.column_dimensions["B"].width = 14

# Prices sheet: downloaded data in A-C, formulas in D-J
ws_p = wb.create_sheet("Prices")
ws_p.append(["Date", "Price (€)", "GBP per EUR", "Value (€)", "Value (£)", "Cash (£)",
             "Daily return", "Drawdown", "Fund index", "Cash index"])
for i, (d, p, f) in enumerate(zip(px.index, px, fx), start=2):
    ws_p.append([
        d.date(), round(float(p), 4), round(float(f), 6),
        f"=B{i}*Summary!$B$7",
        f"=D{i}*C{i}",
        f"=Summary!$B$3*(1+Summary!$B$2)^((A{i}-$A$2)/365)",
        f"=E{i}/E{i-1}-1" if i > 2 else None,
        f"=E{i}/MAX($E$2:E{i})-1",
        f"=E{i}/Summary!$B$9*100",
        f"=F{i}/Summary!$B$3*100",
    ])
    ws_p.cell(i, 1).number_format = "dd/mm/yyyy"
    for col in (7, 8):
        ws_p.cell(i, col).number_format = "0.00%"
    for col in (4, 5, 6, 9, 10):
        ws_p.cell(i, col).number_format = "#,##0.00"
for cell in ws_p[1] + ws_t[1]:
    cell.font = bold
for col in "ABCDEFGHIJ":
    ws_p.column_dimensions[col].width = 13

# Chart: fund vs cash, both starting at 100 so they are comparable
chart = LineChart()
chart.title = "Fund vs cash (100 = amount invested)"
chart.y_axis.title = "Index"
chart.height, chart.width = 9, 18
chart.add_data(Reference(ws_p, min_col=9, max_col=10, min_row=1, max_row=n), titles_from_data=True)
chart.set_categories(Reference(ws_p, min_col=1, min_row=2, max_row=n))
chart.y_axis.scaling.min = 90
ws_s.add_chart(chart, "D2")

wb.move_sheet("Summary", offset=-1)                  # put Summary first
wb.save("tracker.xlsx")
print("\nSaved tracker.csv and tracker.xlsx")
