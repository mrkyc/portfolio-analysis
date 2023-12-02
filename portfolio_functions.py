import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import datetime
import os


# transaction payments column name
TRANSACTION_PAYMENT_COLUMN_NAME = "TRANSACTION_PAYMENT"

# fee payments column name
FEE_PAYMENT_COLUMN_NAME = "FEE_PAYMENT"

# portfolio column name
PORTFOLIO = "PORTFOLIO"

# portfolio data index name
DATE = "DATE"

# suffixes for columns with securities count, value, unit value, expense and profit
COUNT_SUFFIX = "_COUNT"
VALUE_SUFFIX = "_VALUE"
UNIT_VALUE_SUFFIX = "_UNIT_VALUE"
EXPENSE_SUFFIX = "_EXPENSE"
PROFIT_SUFFIX = "_PROFIT"
SINCE_INCEPTION_SUFFIX = "_SINCE_INCEPTION"
VALUE_AND_EXPENSE_SUFFIX = "_VALUE_AND_EXPENSE"
DRAWDOWN_SUFFIX = "_DRAWDOWN"


def generate_plot(
    data, folder_path, column1, column2, title, type, analysis_currency=None
):
    """
    Plot data from data DataFrame and save it to folder_path with title.png name

    Parameters
    ----------
    data : DataFrame
        DataFrame with data to plot
    folder_path : str
        Path to folder where plots will be saved
    column1 : str
        Column name from data DataFrame to plot expense or profit
    column2 : str
        Column name from data DataFrame to plot real value
    title : str
        Title of the plot
    type : str
        Type of the plot to generate (expense_value, profit, drawdown, performance)
    analysis_currency : str
        Currency to analyze (default is None)

    Returns
    -------
    None
    """
    # prepare path to save plot by adding title and extension to folder_path
    path = os.path.join(folder_path, f"{title}.png")

    # set labels and title of the plot
    x_axis_label = "Date"
    y_axis_label = f"Value [{analysis_currency}]" if analysis_currency else "Value"

    # set start and end date of the plot
    start_date = data[column1].dropna().index[0].strftime("%Y-%m-%d")
    end_date = data[column1].dropna().index[-1].strftime("%Y-%m-%d")

    plt.figure(figsize=(10, 6))
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    plt.title(f"{title}\n{start_date} - {end_date}")
    plt.grid(True)

    # plot one line for profit or two lines for expense and value
    if type == "expense_value":
        plt.plot(data.index, data[column1], label="Expense value", color="mediumblue")
        plt.plot(data.index, data[column2], label="Real value", color="darkorange")
        plt.legend()
    elif type == "profit":
        plt.plot(data.index, data[column1], color="darkblue")
        plt.axhline(y=0, color="black", linestyle="--")
    elif type == "drawdown":
        plt.plot(data.index, data[column1], color="dimgray")
        plt.axhline(y=0, color="black", linestyle="--")
    elif type == "performance":
        plt.plot(data.index, data[column1], color="darkgreen")

    plt.savefig(path)
    plt.close()


def create_plots(
    portfolio_data,
    securities_data,
    plots_folder_path,
    analysis_currency,
    securities,
    securities_value,
    securities_expense,
    securities_profit,
):
    """
    Manages plots creation for expenses, values and profits for each security and portfolio as a whole

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    securities_data : DataFrame
        DataFrame with securities data
    plots_folder_path : str
        Path to folder where plots will be saved
    analysis_currency : str
        Currency to analyze
    securities : list
        List of securities names
    securities_value : list
        List of securities value names
    securities_expense : list
        List of securities expense names
    securities_profit : list
        List of securities profit names

    Returns
    -------
    None
    """
    # create plots folder if it does not exist
    if not os.path.exists(plots_folder_path):
        os.makedirs(plots_folder_path)

    # plot for expense and value for each security
    for security_name, security_value, security_expense in zip(
        securities, securities_value, securities_expense
    ):
        generate_plot(
            data=portfolio_data,
            folder_path=plots_folder_path,
            column1=security_expense,
            column2=security_value,
            title=security_name + VALUE_AND_EXPENSE_SUFFIX,
            type="expense_value",
            analysis_currency=analysis_currency,
        )

    # one line plot for profit for each security
    for security_name, security_expense, security_profit in zip(
        securities, securities_expense, securities_profit
    ):
        # take only rows with positive values from expense column to plot only data when security was bought
        # the already bought security has cummulated expense since the first buy
        portfolio_data_truncated = portfolio_data[portfolio_data[security_expense] > 0]

        generate_plot(
            data=portfolio_data_truncated,
            folder_path=plots_folder_path,
            column1=security_profit,
            column2=None,
            title=security_name + PROFIT_SUFFIX,
            type="profit",
            analysis_currency=analysis_currency,
        )

    # plot for profit for portfolio as a whole
    generate_plot(
        data=portfolio_data,
        folder_path=plots_folder_path,
        column1=PORTFOLIO + PROFIT_SUFFIX,
        column2=None,
        title=PORTFOLIO + PROFIT_SUFFIX,
        type="profit",
        analysis_currency=analysis_currency,
    )

    # plot for expense and value for portfolio as a whole
    generate_plot(
        data=portfolio_data,
        folder_path=plots_folder_path,
        column1=PORTFOLIO + EXPENSE_SUFFIX,
        column2=PORTFOLIO + VALUE_SUFFIX,
        title=PORTFOLIO + VALUE_AND_EXPENSE_SUFFIX,
        type="expense_value",
        analysis_currency=analysis_currency,
    )

    # plot portfolio drawdowns
    generate_plot(
        data=portfolio_data,
        folder_path=plots_folder_path,
        column1=PORTFOLIO + DRAWDOWN_SUFFIX,
        column2=None,
        title=PORTFOLIO + DRAWDOWN_SUFFIX,
        type="drawdown",
    )

    # one line plot each security performance
    for security_name in securities:
        generate_plot(
            data=securities_data,
            folder_path=plots_folder_path,
            column1=security_name,
            column2=None,
            title=security_name + SINCE_INCEPTION_SUFFIX,
            type="performance",
            analysis_currency=analysis_currency,
        )


def portfolio_period_to_analysis(
    portfolio_data, analysis_start_date, analysis_end_date
):
    """
    Takes only rows from portfolio_data DataFrame indexed between analysis_start_date and analysis_end_date both included

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    analysis_start_date : str
        Start date of the analysis
    analysis_end_date : str
        End date of the analysis

    Returns
    -------
    DataFrame
        DataFrame with portfolio data for chosen period of time
    """
    start_datetime = datetime.datetime.strptime(analysis_start_date, "%Y-%m-%d")
    end_datetime = datetime.datetime.strptime(analysis_end_date, "%Y-%m-%d")
    portfolio_data = portfolio_data[
        (portfolio_data.index >= start_datetime)
        & (portfolio_data.index <= end_datetime)
    ]

    return portfolio_data


def download_yahoo(tickers, distinct_currencies, ohlc, analysis_currency, securities):
    """
    Downloads data from yahoo finance for tickers and currencies

    Parameters
    ----------
    tickers : list
        List of tickers to download
    distinct_currencies : str
        Currencies to download
    ohlc : str
        Open, High, Low, Close data to download
    analysis_currency : str
        Currency in which the analysis will be done
    securities : list
        List of securities names

    Returns
    -------
    DataFrame
        DataFrame with downloaded data for tickers
    DataFrame
        DataFrame with downloaded exchange rates for currencies
    """
    # convert ohlc to upper case first letter and lower case the rest
    ohlc = ohlc[0].upper() + ohlc[1:].lower()

    # download securities data from yahoo finance
    yahoo_securities_data = yf.download(tickers, period="max")[ohlc]
    df_securities = pd.DataFrame(yahoo_securities_data)

    # set columns order to a specified one in order to correctly set columns names later
    df_securities = df_securities[tickers]

    # set index name to DATE and set columns names to securities names
    df_securities.index.name = DATE
    df_securities.columns = securities

    # create list of currency pairs to download exchange rates for
    distinct_currency_pairs = [
        currency + analysis_currency for currency in distinct_currencies
    ]

    # remove currency pair which is the same as analysis currency
    distinct_currency_pairs.remove(analysis_currency * 2)

    # if currency pairs are specified then download exchange rates for them else set exchange rates to None
    distinct_currency_pairs_format = [
        currency + "=X" for currency in distinct_currency_pairs
    ]

    # download exchange rates from yahoo finance if there are any distinct currency pairs different than analysis currency
    # if distinct_currency_pairs_format:
    yahoo_currencies_data = yf.download(distinct_currency_pairs_format, period="max")[
        ohlc
    ]

    # check if yahoo_currencies_data is a Series or DataFrame
    if isinstance(yahoo_currencies_data, pd.Series):
        # create DataFrame with downloaded exchange rate and set column name to currency pair
        exchange_rates = pd.DataFrame(yahoo_currencies_data)
        exchange_rates.columns = distinct_currency_pairs
    else:
        # set columns order to a specified one in order to correctly set columns names later
        exchange_rates = yahoo_currencies_data[distinct_currency_pairs_format]
        exchange_rates.columns = distinct_currency_pairs

    # if there is analysis currency in distinct currencies then add column with exchange rates equal to 1.0
    if distinct_currencies.index(analysis_currency) != -1:
        analysis_currency_exchange_rates = pd.Series(
            [1.0 for _ in range(len(df_securities.index))],
            index=df_securities.index,
            name=analysis_currency * 2,
        )
        exchange_rates = pd.concat(
            [exchange_rates, analysis_currency_exchange_rates], axis=1
        )

    return df_securities, exchange_rates


def load_portfolio_transactions_data(
    portfolio_data_file_name,
    data_folder_path,
    exchange_rates,
    transaction_payment_list,
    fee_payment_list,
    analysis_currency,
):
    """
    Loads data from .csv file with portfolio transactions data

    Parameters
    ----------
    portfolio_data_file_name : str
        Name of the .csv file with portfolio data
    data_folder_path : str
        Path to folder where portfolio data files are stored
    exchange_rates : DataFrame
        DataFrame with exchange rates
    transaction_payment_list : list
        List with transaction payment column as a first element and its currency as a second element
    fee_payment_list : list
        List with fee payment column as a first element and its currency as a second element
    analysis_currency : str
        Currency which will be used for analysis

    Returns
    -------
    DataFrame
        DataFrame with portfolio transactions data converted to analysis currency
    """
    portfolio_data = pd.read_csv(
        os.path.join(data_folder_path, portfolio_data_file_name),
        index_col=0,
        low_memory=False,
    )
    portfolio_data.index = pd.to_datetime(portfolio_data.index, format="%Y-%m-%d")
    portfolio_data.index.name = DATE

    # convert transaction and fee payments to analysis currency
    transaction_column_name = transaction_payment_list[0]
    fee_column_name = fee_payment_list[0]

    transaction_currency_pair = transaction_payment_list[1] + analysis_currency
    fee_currency_pair = fee_payment_list[1] + analysis_currency

    # convert transaction and fee payments to analysis currency and assign them to a new column
    # to resolve an issue that Pandas cannot reindex on an axis with duplicate labels I will do it in a loop
    for index in portfolio_data.index:
        portfolio_data.loc[index, TRANSACTION_PAYMENT_COLUMN_NAME] = (
            portfolio_data.loc[index, transaction_column_name]
            * exchange_rates.loc[index, transaction_currency_pair]
        )

        portfolio_data.loc[index, FEE_PAYMENT_COLUMN_NAME] = (
            portfolio_data.loc[index, fee_column_name]
            * exchange_rates.loc[index, fee_currency_pair]
        )

    return portfolio_data


def prepare_portfolio_data(
    securities_data,
    exchange_rates,
    transaction_payments,
    fee_payments,
    analysis_currency,
    portfolio_data_files_names_and_payments_columns,
    data_folder_path,
    first_transaction_date,
):
    """
    Prepares portfolio data for analysis

    Parameters
    ----------
    securities_data : DataFrame
        DataFrame with securities data
    exchange_rates : DataFrame
        DataFrame with exchange rates
    transaction_payments : dict
        Dictionary with transaction payments columns and their currencies
    fee_payments : dict
        Dictionary with fee payments columns and their currencies
    analysis_currency : str
        Currency in which the analysis will be done
    portfolio_data_files_names_and_payments_columns : dict
        Dictionary with portfolio data files names and corresponding payments columns (buy/sold and fees)
    data_folder_path : str
        Path to folder where portfolio data files are stored
    first_transaction_date : str
        First transaction date

    Returns
    -------
    DataFrame
        DataFrame with portfolio data prepared for analysis
    """
    # take only rows of DataFrame indexed from first_transaction_date
    securities_data = securities_data[
        securities_data.index
        >= datetime.datetime.strptime(first_transaction_date, "%Y-%m-%d")
    ].copy()

    # fill NaN values with previous values as we assume that if there is no value for a day it means that the stock market was closed that day and the value is the same as the previous day
    securities_data = securities_data.fillna(method="ffill")

    # just in case if there are still NaN values as the first rows of the DataFrame we fill them with 0
    securities_data = securities_data.fillna(0)

    # load portfolio data from .csv files where dates, securities and values of transactions are stored and concatenate them into one DataFrame
    portfolio_data = pd.DataFrame()
    for (
        portfolio_data_file_name,
        payment_columns,
    ) in portfolio_data_files_names_and_payments_columns.items():
        # take column which specifies the transaction payment currency, find a currency and create a list with column name and currency
        transaction_column = payment_columns.get(TRANSACTION_PAYMENT_COLUMN_NAME)
        transaction_currency = transaction_payments.get(transaction_column)
        transaction_payment_list = [transaction_column, transaction_currency]

        # take column which specifies the fee payment currency, find a currency and create a list with column name and currency
        fee_column = payment_columns.get(FEE_PAYMENT_COLUMN_NAME)
        fee_currency = fee_payments.get(fee_column)
        fee_payment_list = [fee_column, fee_currency]

        # load part of portfolio data from .csv file
        portfolio_data_part = load_portfolio_transactions_data(
            portfolio_data_file_name,
            data_folder_path,
            exchange_rates,
            transaction_payment_list,
            fee_payment_list,
            analysis_currency,
        )

        # concatenate part of portfolio data with the rest of portfolio data
        portfolio_data = pd.concat([portfolio_data, portfolio_data_part])

    # merge raw securities data with portfolio data
    portfolio_data = securities_data.join(portfolio_data, rsuffix=COUNT_SUFFIX)

    # sort index in ascending order to ensure that the dates are in the desired order
    portfolio_data = portfolio_data.sort_index()

    return portfolio_data


def print_portfolio_status(
    portfolio_data,
    analysis_currency,
    securities,
    securities_count,
    securities_value,
    securities_expense,
    securities_profit,
):
    """
    Prints portfolio status with current values and profits for each security

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    analysis_currency : str
        Currency to analyze
    securities : list
        List of securities names
    securities_count : list
        List of securities count names
    securities_value : list
        List of securities value names
    securities_expense : list
        List of securities expense names
    securities_profit : list
        List of securities profit names

    Returns
    -------
    None
    """
    # take the last row of portfolio_data DataFrame which is the current portfolio status and calculate profit in percentage
    portfolio_data_current = pd.DataFrame()
    for (
        security_name,
        security_count,
        security_value,
        security_expense,
        security_profit,
    ) in zip(
        securities,
        securities_count,
        securities_value,
        securities_expense,
        securities_profit,
    ):
        new_security_column = portfolio_data[
            [security_count, security_expense, security_value, security_profit]
        ].iloc[-1]

        # calculate profit in percentage
        new_security_column["PROFIT [%]"] = (
            100
            * (
                new_security_column[security_value]
                - new_security_column[security_expense]
            )
            / new_security_column[security_expense]
        )

        new_security_column = pd.DataFrame(
            new_security_column.values, columns=[security_name]
        )
        new_security_column.index = [
            "COUNT",
            "EXPENSE",
            "VALUE",
            "PROFIT",
            "PROFIT [%]",
        ]
        portfolio_data_current = pd.concat(
            [portfolio_data_current, new_security_column], axis=1
        )

    portfolio_data_current.index.name = f"PORTFOLIO STATUS [{analysis_currency}]"
    print(portfolio_data_current.to_markdown(tablefmt="psql", floatfmt=".2f"))


def print_portfolio_weights_and_goal(
    portfolio_data,
    analysis_currency,
    weights,
    weight_groups,
    securities,
    securities_count,
    securities_value,
    securities_unit_value,
):
    """
    Prints portfolio current weights and goal proportions for each security group and portfolio as a whole

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    analysis_currency : str
        Currency to analyze
    weights : dict
        Dictionary with weights for each security group
    weight_groups : dict
        Dictionary with securities names for each security group
    securities : list
        List of securities names
    securities_count : list
        List of securities count names
    securities_value : list
        List of securities value names
    securities_unit_value : list
        List of securities unit value names

    Returns
    -------
    None
    """
    # for storing current value for each weights group
    weight_groups_current_values = {}

    # calculate current values for each weights group
    for security_name, security_value in zip(securities, securities_value):
        security_current_value = portfolio_data[security_value].iloc[-1]
        weight_group = [
            key for key, value in weight_groups.items() if security_name in value
        ][0]
        weight_groups_current_values.update(
            {
                weight_group: security_current_value
                + weight_groups_current_values.get(weight_group, 0)
            }
        )

    # take current portfolio value
    portfolio_current_value = portfolio_data[PORTFOLIO + VALUE_SUFFIX].iloc[-1]

    # for storing current weight deviation for each weights group
    weight_groups_current_deviation = {}

    # calculate current weights for each weights group and deviation from ideal weights by subtracting current weight from ideal weight
    portfolio_current_weights = pd.DataFrame()
    for weight_group_name, weight_group_values in weight_groups_current_values.items():
        current_share = 100 * weight_group_values / portfolio_current_value
        deviation = current_share - weights.get(weight_group_name)
        weight_groups_current_deviation.update({weight_group_name: deviation})
        deviation_str = f"{deviation:.2f}" if deviation < 0 else f" {deviation:.2f}"

        # create DataFrame with current weight for a given weight group
        weight_group_dataframe = pd.DataFrame(
            [
                current_share,
                deviation_str,
                portfolio_current_value * weights.get(weight_group_name) / 100,
                weight_group_values,
            ],
            columns=[weight_group_name],
            index=["SHARE [%]", "DEVIATION [% pts]", "IDEAL VALUE", "CURRENT VALUE"],
        )

        # concatenate DataFrame with current weight for a given weight group with DataFrame with current weights for all weight groups
        portfolio_current_weights = pd.concat(
            [portfolio_current_weights, pd.DataFrame(weight_group_dataframe)], axis=1
        )

    portfolio_current_weights.index.name = (
        f"PORTFOLIO CURRENT WEIGHTS [{analysis_currency}]"
    )
    print(portfolio_current_weights.to_markdown(tablefmt="psql", floatfmt=".2f"))

    # find weight group with the biggest (positive) deviation from ideal weight
    # this weight group will be used to calculate new goal values
    max_deviation_weight_group = max(
        weight_groups_current_deviation,
        key=lambda key: weight_groups_current_deviation.get(key) / weights.get(key),
    )

    # calculate new goal p.p. value for the weight group with the biggest deviation from ideal weight
    # new goal p.p. value is calculated by dividing current value for the weight group with the biggest (positive) deviation from ideal weight by ideal weight for that weight group
    # it results with a new goal percentage point which will be used to calculate new goal values for each weight group
    new_goal_percentage_point_value = weight_groups_current_values.get(
        max_deviation_weight_group
    ) / weights.get(max_deviation_weight_group)

    # calculate new goal values and counts for each weight group and its securities
    portfolio_new_goal = pd.DataFrame()
    for weight_group_name, weight_group_securities in weight_groups.items():
        new_goal_value = new_goal_percentage_point_value * weights.get(
            weight_group_name
        )

        # for storing new goal count and current count for each security in a given weight group
        weight_groups_securities_counts_dict = {}

        # take indexes of securities in securities list
        weight_group_securities_indexes = [
            securities.index(security) for security in weight_group_securities
        ]

        # calculate current value for a given securities weight group
        weight_group_securities_current_value = 0
        for index in weight_group_securities_indexes:
            weight_group_securities_current_value += portfolio_data[
                securities_value[index]
            ].iloc[-1]

        # calculate new goal count and current count for each security in a given weight group
        for weight_group_security in weight_group_securities:
            if weight_group_security not in securities:
                continue

            # find index of a given security in securities list
            list_index_of_security = securities.index(weight_group_security)

            # take security unit value column name
            security_unit_value = securities_unit_value[list_index_of_security]

            # calculate new goal count for a given security by taking the lacking value of securities to meet the desired weight divided by current unit value of a given security
            new_goal_approximated_count = (
                new_goal_value - weight_group_securities_current_value
            ) / portfolio_data[security_unit_value].iloc[-1]

            # take security count column name
            security_count = securities_count[list_index_of_security]

            # take current count for a given security
            security_current_count = portfolio_data[security_count].iloc[-1]

            # add new goal count and current count for a given security to dictionary
            weight_groups_securities_counts_dict.update(
                {
                    weight_group_security: [
                        new_goal_approximated_count,
                        security_current_count,
                    ]
                }
            )

        # add new goal value and current value for a given weight group to list
        weight_group_name_values_list = [
            new_goal_value,
            weight_groups_current_values.get(weight_group_name),
        ]

        # string with new goal count for each security in a given weight group
        goal_count = ""

        # string with current count for each security in a given weight group
        current_count = ""

        # for each security in a given weight group add new goal count and current count to strings
        for key, value in weight_groups_securities_counts_dict.items():
            goal_count += f"{key}: {value[0]:.2f}\n"
            current_count += f"{key}: {value[1]}\n"

        # create DataFrame with new goal values, current values, new goal count and current count for a given weight group
        weight_group_dataframe = pd.DataFrame(
            [
                round(weight_group_name_values_list[0], 2),  # new goal value
                round(weight_group_name_values_list[1], 2),  # current value
                goal_count,
                current_count,
            ],
            columns=[weight_group_name],
            index=["VALUE", "CURRENT VALUE", "COUNT TO BUY", "CURRENT COUNT"],
        )

        # concatenate new goals DataFrame for a given weight group with new goals DataFrame for all weight groups
        portfolio_new_goal = pd.concat(
            [portfolio_new_goal, pd.DataFrame(weight_group_dataframe)], axis=1
        )

    # new portfolio goal value is calculated by multiplying new goal p.p. value by 100
    goal_sum = round(new_goal_percentage_point_value * 100, 2)

    # concatenate new goals DataFrame for all weight groups with DataFrame with portfolio's new goal value and current value
    portfolio_new_goal = pd.concat(
        [
            portfolio_new_goal,
            pd.DataFrame(
                [goal_sum, round(portfolio_current_value, 2), *2 * [""]],
                columns=["SUM"],
                index=["VALUE", "CURRENT VALUE", "COUNT TO BUY", "CURRENT COUNT"],
            ),
        ],
        axis=1,
    )
    portfolio_new_goal.index.name = f"GOAL [{analysis_currency}]"
    print(portfolio_new_goal.to_markdown(tablefmt="psql", floatfmt=".2f"))


def print_portfolio_performance(portfolio_data, analysis_currency):
    """
    Prints portfolio performance with current value, expense, profit and profit in percentage

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    analysis_currency : str
        Currency of the analysis

    Returns
    -------
    None
    """
    # take current portfolio value and expense
    portfolio_current_value = portfolio_data[PORTFOLIO + VALUE_SUFFIX].iloc[-1]
    portfolio_current_expense = portfolio_data[PORTFOLIO + EXPENSE_SUFFIX].iloc[-1]

    # create DataFrame with portfolio performance
    portfolio_performance = pd.DataFrame(
        [
            portfolio_current_value,
            portfolio_current_expense,
            portfolio_current_value - portfolio_current_expense,
            100
            * (portfolio_current_value - portfolio_current_expense)
            / portfolio_current_expense,
        ],
        columns=["VALUES"],
        index=["VALUE", "EXPENSE", "PROFIT", "PROFIT [%]"],
    )
    portfolio_performance.index.name = f"PORTFOLIO PERFORMANCE [{analysis_currency}]"
    print(portfolio_performance.to_markdown(tablefmt="psql", floatfmt=".2f"))


def calculate_portfolio_values(
    portfolio_data,
    securities,
    securities_count,
    securities_value,
    securities_unit_value,
    securities_expense,
    securities_profit,
):
    """
    Calculates portfolio components' property values for each security and portfolio as a whole and adds them to portfolio_data DataFrame

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    securities : list
        List of securities names
    securities_count : list
        List of securities count names
    securities_value : list
        List of securities value names
    securities_unit_value : list
        List of securities unit value names
    securities_expense : list
        List of securities expense names
    securities_profit : list
        List of securities profit names

    Returns
    -------
    DataFrame
        DataFrame with portfolio data with calculated values
    """
    # assign values from securities_count to securities_value and securities_expense as values and expenses will be calculated later using these count values
    portfolio_data[securities_value] = portfolio_data[securities_count]
    portfolio_data[securities_expense] = portfolio_data[securities_count]

    # rename columns to more informative names
    portfolio_data = portfolio_data.rename(
        columns=dict(zip(securities, securities_unit_value))
    )

    # temporarily reset index to get rid of duplicate index values
    portfolio_data = portfolio_data.reset_index()

    # security expense without transaction fee
    for security_expense in securities_expense:
        portfolio_data[security_expense] = portfolio_data[
            portfolio_data[security_expense] > 0
        ][TRANSACTION_PAYMENT_COLUMN_NAME]

    # set index back to DATE
    portfolio_data = portfolio_data.set_index(DATE)

    # separate securities unit values from other columns and drop duplicates in DATE column from these separated securities unit values
    duplicated_idx = portfolio_data.index.duplicated()
    unit_values_data = portfolio_data.loc[~duplicated_idx, securities_unit_value].copy()

    # drop securities unit values from portfolio_data DataFrame
    portfolio_data = portfolio_data.drop(securities_unit_value, axis=1)

    # group by DATE and sum all the values for each DATE
    portfolio_data = portfolio_data.groupby(DATE).sum()

    # join portfolio_data DataFrame with separated earlier securities unit values
    portfolio_data = portfolio_data.join(unit_values_data)

    # currently in securities values there is only count of securities securities as an auxiliary column to calculate portfolio values later
    # we fill NaN values with 0 and calculate cummulative sum to get the number of securities in the portfolio at a given time
    portfolio_data[securities_value] = (
        portfolio_data[securities_value].fillna(0).cumsum()
    )

    # calculate portfolio values for each security using currently stored count of securities and unit value
    for security_value, security_unit_value in zip(
        securities_value, securities_unit_value
    ):
        portfolio_data[security_value] = (
            portfolio_data[security_value] * portfolio_data[security_unit_value]
        )

    # fill all the remaining NaN values with 0
    portfolio_data = portfolio_data.fillna(0)

    # calculate cummulative sum of expenses and count of securities
    portfolio_data[securities_expense] = portfolio_data[securities_expense].cumsum()
    portfolio_data[securities_count] = portfolio_data[securities_count].cumsum()

    # add fees to transaction payments
    portfolio_data[TRANSACTION_PAYMENT_COLUMN_NAME] = (
        portfolio_data[TRANSACTION_PAYMENT_COLUMN_NAME]
        + portfolio_data[FEE_PAYMENT_COLUMN_NAME]
    )

    # calculate cummulative sum of portfolio expenses as a sum of transaction payments and fees
    portfolio_data[PORTFOLIO + EXPENSE_SUFFIX] = portfolio_data[
        TRANSACTION_PAYMENT_COLUMN_NAME
    ].cumsum()

    # calculate portfolio value as a sum of securities values
    portfolio_data[PORTFOLIO + VALUE_SUFFIX] = portfolio_data[securities_value].sum(
        axis=1
    )

    # calculate portfolio profit as a difference between portfolio value and portfolio expense
    portfolio_data[PORTFOLIO + PROFIT_SUFFIX] = (
        portfolio_data[PORTFOLIO + VALUE_SUFFIX]
        - portfolio_data[PORTFOLIO + EXPENSE_SUFFIX]
    )

    # calculate profit for each security as a difference between security value and security expense
    for security_value, security_expense, security_profit in zip(
        securities_value, securities_expense, securities_profit
    ):
        portfolio_data[security_profit] = (
            portfolio_data[security_value] - portfolio_data[security_expense]
        )

    # calculate portfolio drawdowns
    for date in portfolio_data.index:
        max_value = portfolio_data.loc[:date, PORTFOLIO + VALUE_SUFFIX].max()
        current_value = portfolio_data.loc[date, PORTFOLIO + VALUE_SUFFIX]

        if max_value == 0:
            portfolio_data.loc[date, PORTFOLIO + DRAWDOWN_SUFFIX] = 0
            continue

        portfolio_data.loc[date, PORTFOLIO + DRAWDOWN_SUFFIX] = (
            current_value - max_value
        ) / max_value

    # concatenate columns to leave into one list
    columns_to_leave = [
        securities_count
        + securities_value
        + securities_unit_value
        + securities_expense
        + securities_profit
        + [
            PORTFOLIO + VALUE_SUFFIX,
            PORTFOLIO + EXPENSE_SUFFIX,
            PORTFOLIO + PROFIT_SUFFIX,
            PORTFOLIO + DRAWDOWN_SUFFIX,
        ]
    ]

    # leave only specified columns
    portfolio_data = portfolio_data[columns_to_leave[0]]

    return portfolio_data


def portfolio_analysis(
    portfolio_data,
    securities_data,
    analysis_currency,
    securities,
    weights,
    weights_groups,
    analysis_start_date,
    analysis_end_date,
    plots_folder_path,
):
    """
    Manages portfolio analysis

    Parameters
    ----------
    portfolio_data : DataFrame
        DataFrame with portfolio data
    securities_data : DataFrame
        DataFrame with securities data
    analysis_currency : str
        Currency to analyze
    securities : list
        List of securities names
    weights : dict
        Dictionary with weights for each security group
    weights_groups : dict
        Dictionary with securities names for each security group
    analysis_start_date : str
        Start date of the analysis
    analysis_end_date : str
        End date of the analysis
    plots_folder_path : str
        Path to folder where plots will be saved

    Returns
    -------
    None
    """
    # list of columns for portfolio different values for each security
    securities_count = [col + COUNT_SUFFIX for col in securities]
    securities_value = [col + VALUE_SUFFIX for col in securities]
    securities_unit_value = [col + UNIT_VALUE_SUFFIX for col in securities]
    securities_expense = [col + EXPENSE_SUFFIX for col in securities]
    securities_profit = [col + PROFIT_SUFFIX for col in securities]

    # calculate portfolio values, expenses, profits, etc. for each security since the first transaction date
    portfolio_data = calculate_portfolio_values(
        portfolio_data,
        securities,
        securities_count,
        securities_value,
        securities_unit_value,
        securities_expense,
        securities_profit,
    )

    # take portfolio data only from the analysis period
    portfolio_data = portfolio_period_to_analysis(
        portfolio_data, analysis_start_date, analysis_end_date
    )

    # print portfolio status at the end of the analysis period
    print_portfolio_status(
        portfolio_data,
        analysis_currency,
        securities,
        securities_count,
        securities_value,
        securities_expense,
        securities_profit,
    )

    # print portfolio current weights compared to the model weights and accumulation goal (so what should be bought to meet the desired weights without selling anything)
    print_portfolio_weights_and_goal(
        portfolio_data,
        analysis_currency,
        weights,
        weights_groups,
        securities,
        securities_count,
        securities_value,
        securities_unit_value,
    )

    # print portfolio performance summary
    print_portfolio_performance(portfolio_data, analysis_currency)

    # create plots for portfolio
    create_plots(
        portfolio_data,
        securities_data,
        plots_folder_path,
        analysis_currency,
        securities,
        securities_value,
        securities_expense,
        securities_profit,
    )
