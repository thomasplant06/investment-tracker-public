# investment-tracker-public

A Python script that compares a fund holding against a cash benchmark, using a local trades.csv file.

## What it does
- Downloads the fund's price history from Yahoo Finance (ticker V40A.AS)
- Calculates the value of the holding, return, volatility and drawdown
- Compares the holding with cash converted to euros

## Running it
1. Create a `trades.csv` file with columns: date, asset, units, price, fees, total
2. Upload `tracker.py` and `trades.csv` to Google Colab
3. Run the script

The trades file is not included, because it contains personal financial records.

This project is for learning and is not investment advice.
