from portfolio_functions import *


def main():
    # ------------------- portfolio parameters ------------------- #

    # currency in which the portfolio data will be analyzed
    analysis_currency = "EUR"

    # tickers and the corresponding currencies of securities in portfolio to download from yahoo finance
    tickers_and_currencies = {
        "VWCE.DE": "EUR",
        "ISAC.L": "USD",
        "VAGP.L": "GBP",
        "SAGG.L": "GBP",
        "4GLD.DE": "EUR",
        "IGLN.L": "USD",
    }

    # allocation of securities in portfolio in percentages
    weights = {"STOCKS": 50, "BONDS": 30, "GOLD": 20}

    # securities groups
    weight_groups = {
        "STOCKS": ["VWCE", "ISAC"],
        "BONDS": ["VAGP", "SAGG"],
        "GOLD": ["4GLD", "IGLN"],
    }

    # path to folder with portfolio data files
    data_folder_path = "data"

    # portfolio data files
    portfolio_data_files_names_and_payments_columns = {
        "portfolio_broker1.csv": {
            "TRANSACTION_PAYMENT": "transaction",
            "FEE_PAYMENT": "trx_fee",
        },
        "portfolio_broker2.csv": {
            "TRANSACTION_PAYMENT": "transactions",
            "FEE_PAYMENT": "fees",
        },
        "portfolio_broker3.csv": {
            "TRANSACTION_PAYMENT": "trx_values",
            "FEE_PAYMENT": "fees",
        },
    }

    # transaction payments dictionary
    # key is a column name where the transaction payment is stored in portfolio files
    # value is a currency of the payment
    transaction_payments = {
        "transaction": "EUR",
        "transactions": "EUR",
        "trx_values": "EUR",
    }
    fee_payments = {"trx_fee": "EUR", "fees": "EUR"}

    # first transaction date to calculate portfolio values from this date
    # using this variable we can calculate portfolio values from the real beginning of the portfolio or with omitting some of the first transactions if needed
    first_transaction_date = "2019-07-29"

    # analysis start and end date to take portfolio values only from this period
    # start date should be the same or later than first_transaction_date
    start_date = "2019-07-29"
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # which column to use for open, high, low, close prices
    ohlc = "close"

    # folder path to save plots
    plots_folder_path = "portfolio plots"

    # ------------------- portfolio analysis ------------------- #

    # take securities names from tickers_and_currencies dictionary
    securities = [
        security_name.split(".")[0] for security_name in tickers_and_currencies
    ]

    # take tickers and currencies from tickers_and_currencies dictionary
    tickers = [*tickers_and_currencies.keys()]
    currencies_securities = [*tickers_and_currencies.values()]

    # take currencies from transaction_payments dictionary
    currencies_transation_payments = [*transaction_payments.values()]

    # take currencies from fee_payments dictionary
    currencies_fee_payments = [*fee_payments.values()]

    # combine currencies of securities and payments
    currencies = (
        currencies_securities + currencies_transation_payments + currencies_fee_payments
    )

    # take distinct currencies
    distinct_currencies = list(set(currencies))

    # download securities data and exchange rates from yahoo finance in a daily frequency
    securities_data, exchange_rates = download_yahoo(
        tickers, distinct_currencies, ohlc, analysis_currency, securities
    )

    # calculate values of securities in analysis currency
    for ticker, currency in tickers_and_currencies.items():
        security_name = ticker.split(".")[0]
        currency_pair = currency + analysis_currency
        securities_data[security_name] = (
            securities_data[security_name] * exchange_rates[currency_pair]
        )

    # prepare portfolio data for analysis using downloaded data and portfolio data files
    portfolio_data = prepare_portfolio_data(
        securities_data,
        exchange_rates,
        transaction_payments,
        fee_payments,
        analysis_currency,
        portfolio_data_files_names_and_payments_columns,
        data_folder_path,
        first_transaction_date,
    )

    # run portfolio analysis
    portfolio_analysis(
        portfolio_data,
        securities_data,
        analysis_currency,
        securities,
        weights,
        weight_groups,
        start_date,
        end_date,
        plots_folder_path,
    )


if __name__ == "__main__":
    main()
