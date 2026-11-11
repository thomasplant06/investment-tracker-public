import pandas as pd, numpy as np, yfinance as yf
import xlsxwriter

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
# Each formula is written with its calculated value as well, so the numbers
# show up in previews and viewers that do not calculate formulas themselves.
wb = xlsxwriter.Workbook("tracker.xlsx")
ws_s = wb.add_worksheet("Summary")
ws_t = wb.add_worksheet("Trades")
ws_p = wb.add_worksheet("Prices")
bold = wb.add_format({"bold": True})
fmt = lambda f, **kw: wb.add_format({"num_format": f, **kw})

# Trades sheet: a copy of trades.csv
ws_t.write_row(0, 0, trades.columns, bold)
for r, row in enumerate(trades.itertuples(index=False), start=1):
    ws_t.write_row(r, 0, row)
ws_t.set_column("A:F", 14)

# Summary sheet: inputs at the top (blue = you can change them), results underneath
n = len(px) + 1                                      # last data row on Prices
rows = [
    ("INPUTS", None, None, None),
    ("Cash rate (AER)", CASH_RATE, "0.00%", None),
    ("Cash benchmark (£)", GBP_CASH, "£#,##0.00", None),
    ("EUR per GBP at purchase", TRADE_EUR_PER_GBP, "0.0000", None),
    (None, None, None, None),
    ("HOLDING", None, None, None),
    ("Units held", "=SUM(Trades!C:C)", "0.0000", units),
    ("Cost (€, incl. fees)", "=SUM(Trades!F:F)", "€#,##0.00", cost_eur),
    ("Cost (£)", "=B8/B4", "£#,##0.00", cost_gbp),
    ("Latest value (€)", f"=Prices!D{n}", "€#,##0.00", value_eur.iloc[-1]),
    ("Latest value (£)", f"=Prices!E{n}", "£#,##0.00", value_gbp.iloc[-1]),
    (None, None, None, None),
    ("PERFORMANCE", None, None, None),
    ("Fund return in euros", "=B10/B8-1", "0.00%", fund_ret_eur),
    ("Currency effect (EUR vs GBP)", f"=Prices!C{n}*B4-1", "0.00%", fx_ret),
    ("Total return in pounds", "=B11/B9-1", "0.00%", total_ret_gbp),
    ("Cash benchmark return", f"=Prices!F{n}/B3-1", "0.00%", cash_ret),
    ("Fund minus cash", "=B16-B17", "0.00%", total_ret_gbp - cash_ret),
    (None, None, None, None),
    ("RISK", None, None, None),
    ("Annualised volatility", f"=STDEV(Prices!G3:G{n})*SQRT(252)", "0.00%", daily_ret.std() * np.sqrt(252)),
    ("Maximum drawdown", f"=MIN(Prices!H2:H{n})", "0.00%", drawdown.min()),
]
for r, (label, val, f, result) in enumerate(rows):
    if val is None:
        ws_s.write(r, 0, label, bold)
    elif result is None:
        ws_s.write(r, 0, label)
        ws_s.write(r, 1, val, fmt(f, font_color="#0000FF"))
    else:
        ws_s.write(r, 0, label)
        ws_s.write_formula(r, 1, val, fmt(f), float(result))
ws_s.set_column("A:A", 30)
ws_s.set_column("B:B", 14)

# Prices sheet: downloaded data in A-C, formulas in D-J
ws_p.write_row(0, 0, ["Date", "Price (€)", "GBP per EUR", "Value (€)", "Value (£)", "Cash (£)",
                      "Daily return", "Drawdown", "Fund index", "Cash index"], bold)
date_f, num_f, pct_f = fmt("dd/mm/yyyy"), fmt("#,##0.00"), fmt("0.00%")
for k in range(len(px)):
    i = k + 2                                        # Excel row number
    ws_p.write_datetime(k + 1, 0, px.index[k].to_pydatetime(), date_f)
    ws_p.write(k + 1, 1, round(float(px.iloc[k]), 4))
    ws_p.write(k + 1, 2, round(float(fx.iloc[k]), 6))
    ws_p.write_formula(k + 1, 3, f"=B{i}*Summary!$B$7", num_f, float(value_eur.iloc[k]))
    ws_p.write_formula(k + 1, 4, f"=D{i}*C{i}", num_f, float(value_gbp.iloc[k]))
    ws_p.write_formula(k + 1, 5, f"=Summary!$B$3*(1+Summary!$B$2)^((A{i}-$A$2)/365)", num_f, float(cash_gbp.iloc[k]))
    if k > 0:
        ws_p.write_formula(k + 1, 6, f"=E{i}/E{i-1}-1", pct_f, float(daily_ret.iloc[k - 1]))
    ws_p.write_formula(k + 1, 7, f"=E{i}/MAX($E$2:E{i})-1", pct_f, float(drawdown.iloc[k]))
    ws_p.write_formula(k + 1, 8, f"=E{i}/Summary!$B$9*100", num_f, float(value_gbp.iloc[k] / cost_gbp * 100))
    ws_p.write_formula(k + 1, 9, f"=F{i}/Summary!$B$3*100", num_f, float(cash_gbp.iloc[k] / GBP_CASH * 100))
ws_p.set_column("A:J", 13)

# Chart: fund vs cash, both starting at 100 so they are comparable
chart = wb.add_chart({"type": "line"})
for col, name in ((8, "Fund index"), (9, "Cash index")):
    chart.add_series({"name": name,
                      "categories": ["Prices", 1, 0, n - 1, 0],
                      "values": ["Prices", 1, col, n - 1, col]})
chart.set_title({"name": "Fund vs cash (100 = amount invested)"})
chart.set_y_axis({"name": "Index", "min": 90})
chart.set_x_axis({"date_axis": True, "num_format": "dd mmm"})
chart.set_legend({"position": "bottom"})
chart.set_size({"width": 620, "height": 340})
ws_s.insert_chart("D2", chart)

wb.close()
print("\nSaved tracker.csv and tracker.xlsx")
