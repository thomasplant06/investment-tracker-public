# investment-tracker-public

A small Python project that tracks a £2,000 holding in Vanguard LifeStrategy 40% Equity, a euro-listed multi-asset fund (roughly 40% equities and 60% bonds), against a cash benchmark, to test my own investment reasoning over time.

## What it does

- Downloads daily price history for the fund from Yahoo Finance (ticker `V40A.AS`)
- Downloads the daily EUR/GBP exchange rate, so returns are reported in pounds
- Values my holding using the units and prices in `trades.csv`
- Splits my sterling return into what the fund did in euros and the effect of converting euros into pounds
- Compares the holding with a £500 cash benchmark earning 4% AER
- Calculates total return net of fees, annualised volatility and maximum drawdown
- Writes a daily history to `tracker.csv` and an Excel workbook, `tracker.xlsx`

## Files

- `tracker.py`: the script
- `trades.csv`: my trade log (date, asset, units, price, fees, total)
- `tracker.xlsx`: the output workbook. The Summary sheet has the inputs, results and a fund-versus-cash chart; the results are live Excel formulas that read from the Trades and Prices sheets
- `tracker.csv`: the same daily history as plain text
- `.github/workflows/update.yml`: runs the script on GitHub and saves the output back to this repository

## Running it

On GitHub: open the Actions tab, choose "Update tracker" and click "Run workflow".

In Google Colab:

1. Open a new notebook in Google Colab (colab.research.google.com).
2. In the first cell, run `!pip install yfinance xlsxwriter`.
3. Upload `trades.csv` to the Colab Files panel.
4. Paste `tracker.py` into a second cell and set `CASH_RATE` to the AER of your cash account, if it differs from 4%.
5. Run the cell. It prints a summary and saves `tracker.csv` and `tracker.xlsx`, which you can download from the Files panel.

## Notes

- The fund is priced in euros but I think in pounds, so the script converts the holding at each day's exchange rate. The cash benchmark stays in pounds.
- The currency split measures only the effect of converting the euro price into pounds. The fund's euro price already reflects currency moves in its underlying holdings, so this is not the fund's full currency exposure.
- Volatility and drawdown are measured on the pound value of the holding, and only become meaningful after several months of data.
- This is a learning project, not investment advice.
