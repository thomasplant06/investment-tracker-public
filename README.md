# investment-tracker-public

A small Python project that tracks a £2,000 holding in a euro-listed global equity fund against a cash benchmark, to test my own investment reasoning over time.

## What it does

- Downloads daily price history for the fund from Yahoo Finance (ticker `V40A.AS`)
- Downloads the daily EUR/GBP exchange rate, so returns are reported in pounds
- Values my holding using the units and prices in `trades.csv`
- Splits my return into what the fund did (in euros) and what the currency did
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

1. Open `tracker.py` in Google Colab (colab.research.google.com).
2. Upload `trades.csv` to the Colab Files panel.
3. Set `CASH_RATE` to the AER of your cash account, if it differs from 4%.
4. Run the cell. It prints a summary and saves `tracker.csv` and `tracker.xlsx`.

## Notes

- The fund is priced in euros but I think in pounds, so the script converts the holding at each day's exchange rate. The cash benchmark stays in pounds.
- Volatility and drawdown are measured on the pound value of the holding, and only become meaningful after several months of data.
- This is a learning project, not investment advice.
