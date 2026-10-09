# investment-tracker-public

A small Python project that tracks a £2,000 holding in a euro-listed global equity fund against a cash benchmark, to test my own investment reasoning over time.

## What it does

- Downloads daily price history for the fund from Yahoo Finance (ticker `V40A.AS`)
- Values my holding using the units and prices in `trades.csv`
- Compares the holding with a £500 cash benchmark, converted to euros
- Calculates total return, annualised volatility and maximum drawdown
- Writes a weekly history to `tracker.csv`

## Files

- `tracker.py`: the script
- `trades.csv`: my trade log (date, asset, units, price, fees, total)

## Running it

1. Open `tracker.py` in Google Colab (colab.research.google.com).
2. Upload `trades.csv` to the Colab Files panel.
3. Set `CASH_RATE` to the AER of your cash account, if it differs from 4%.
4. Run the cell. It prints a summary and saves `tracker.csv`.

## Notes

- Prices are in euros, so the cash benchmark is converted at the same rate used for the trades.
- Volatility and drawdown only become meaningful after several months of weekly runs.
- This is a learning project, not investment advice.
