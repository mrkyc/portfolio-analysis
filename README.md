# portfolio-analysis

Analysis and monitoring of the investment portfolio.

## Table of Contents

1. [Overview](#overview)
2. [Usage](#usage)
3. [Examples](#examples)

## Overview

Based on the provided portfolio `.csv` files, the code calculates values such as securities value and profit over time. It converts all data to a specified **analysis currency** to facilitate the analysis. Additionally, it generates analysis plots described below.

It is mainly intended for portfolios consisting of ETFs. Therefore, I will use ETFs in examples below.

The data for analysis comes from Yahoo Finance, and it is retrieved using the yfinance library.

### Console tables

Code prints four console tables:

1. Portfolio current status

   The columns in the table represent each security held in the portfolio. Rows indicates:

   - **count** - Number of units of a given security.
   - **expense** - Sum of expenses for a specific security (without fees that can be specified in the dedicated column).
   - **value** - Current value of the corresponding security position.
   - **profit** - Current profit from that position.
   - **percentage profit** - Current percentage profit from the respective security position.

2. Portfolio current weights

   Security weight groups in column. Rows indicates:

   - **share** - Current share in the portfolio.
   - **deviation from model weights** - The difference between model weights and current weights.
   - **ideal value** - The ideal (model) value.
   - **current value** - Sum of current values of securities in a given group.

3. Portfolio accumulation goals

   This table is intended to facilitate the realization of a buy-and-hold strategy, emphasizing the intention to refrain from selling any securities. Instead, the objective is to acquire a specific count of securities to align with the model weights. The weight groups are represented as columns. Additionally, there is an extra column _SUM_ which tells what is the value of the portfolio currently, and what will be its value if we will reach the goal. The rows consist of:

   - **value** - Goal value of a group.
   - **current value** - Sum of current values of securities in a given group.
   - **count to buy** - The amount of units of a specific security to buy is determined in order to meet the goal weight group value. If there is more than one security name in a group, it indicates the units amount for each of them, and buying one of the corresponding amount of them will meet the goal.
   - **current count** - Current units amount of a given security.

4. Portfolio performance

   This table presents the current status of the portfolio as a whole.
   It consists of a single column with values corresponding to rows. The rows indicate:

   - **value** - Current value of the sum of all securities values in the portfolio.
   - **expense** - Total cost of securities (with fees if specified in the dedicated column).
   - **profit** - Total portfolio profit.
   - **percentage profit** - Total portfolio percentage profit.

### Plots

The code generates the following plots:

1. Portfolio profit over time plot
2. Portfolio values and expenses over time plot
3. Portfolio drawdowns over time plot
4. Profit plot for each security in portfolio
5. Values and expenses for each security in portfolio
6. Values of each security since its inception

## Usage

In order to use the code you have to specify initial parameters in `portfolio.py` file.

The following parameters should be considered:

- `analysis_currency` - The currency in which the analysis will be performed.
- `tickers_and_currencies` - A dictionary where the keys are for securities tickers and the values are for currencies for the corresponding securities.
- `weights` - A dictionary conatining weight groups names as keys and the securities name list (tickers characters before the dot) as the corresponding values.
- `portfolio_data_files_paths_and_payments_columns` - A dictionary with paths to portfolio files as keys. The values are smaller dictionaries, each containing two key-value pairs. The first pair has the key **_TRANSACTION_PAYMENT_**, and the corresponding value is the column name in the portfolio file representing transaction payments (buy/sell) without broker fees. The second pair has the key **_FEE_PAYMENT_**, and the corresponding value is the column name in the portfolio file representing fees payment for transactions.
- `transaction_payments` - A dictionary with the columns from portfolio data files specified as **_TRANSACTION_PAYMENT_** as keys. The values are the corresponding currencies in which the amount is specified.
- `fee_payments` - A dictionary with the columns from portfolio data files specified as **_FEE_PAYMENT_** as keys. The values are the corresponding currencies in which the amount is specified.
- `first_transaction_date` - The date of the first transaction in portfolio.
- `start_date` - Start date of the analysis is used to shorten the period of analysis. It does not influence the values themselves, just drop the earlier dates before the output. Must be equal or older than the **_first_transaction_date_** date.
- `end_date` - End date of the analysis is used to shorten the period of analysis by ending on the specified date. The printed tables will show the portfolio's and its components' states for that date.
- `ohlc` - Which of the open, high, low or close from the downloaded data should be used in analysis
- `plots_folder_path` - The folder where the plots will be saved. It will be created if does not exist.

## Examples

The code already includes predefined sample parameters and randomly generated portfolio data files. This should help you better understand the code concepts.

### Predefined portfolio strategy

Each calendar month we buy specified securities (ETFs) in the corresponding weights for ~1000 euro.

We will invest in the securities (ETFs) below:

- `VWCE.DE` - Vanguard FTSE All-World UCITS ETF - currency: `EUR`
- `ISAC.L` - iShares MSCI ACWI UCITS ETF USD - currency: `USD`
- `VAGP.L` - Vanguard Global Aggregate Bond UCITS ETF - currency: `GBP`
- `SAGG.L` - iShares Core Global Aggregate Bond UCITS ETF - currency: `GBP`
- `4GLD.DE` - Xetra-Gold - currency: `EUR`
- `IGLN.L` - iShares Physical Gold ETC - currency: `USD`

We have 3 brokerage accounts, so we keep transactions in 3 different files to distinguish them.
For a given broker, we buy securities according to the following tickers.
For broker:

- number 1: `VWCE.DE`, `4GLD.DE`. Additional fee 4 euro per transaction.
- number 2: `VAGP.L`, `SAGG.L`. Additional fee 3 euro per transaction.
- number 3: `ISAC.L`, `IGLN.L`. Additional fee 3 euro per transaction.

Transaction data from each broker is stored in the following portfolio data files:

1. `portfolio_broker1.csv` - for broker number 1.
2. `portfolio_broker2.csv` - for broker number 2.
3. `portfolio_broker3.csv` - for broker number 3.

Some files have different column names for transaction payments and fees. In our case, it's just about showing that the code can work with them. Mainly it would be used if we had different transaction currencies. In our case, we use euros in each brokerage account.
Therefore we specify:

- `transaction_payments` to be:
  - `"transaction": "EUR"`,
  - `"transactions": "EUR"`,
  - `"trx_values": "EUR"`
- `fee_payments`:
  - `"trx_fee": "EUR"`,
  - `"fees": "EUR"`

Our portfolio has the following weight groups:

- **STOCKS** 50% consisting of: `VWCE.DE`, `ISAC.L`
- **BONDS** 30% consisting of: `VAGP.L`, `SAGG.L`
- **GOLD** 20% consisting of: `4GLD.DE`, `IGLN.L`

The date of the first transaction was `2019-07-29`. The analysis will be carried out in the period from `2019-07-29` to `2023-11-25`. We will analyse close prices as they are usually the best for such analysis. The folder for plots will be named `portfolio plots`.

### Results

#### Tables:

##### Portfolio current status

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/812cf5f6-7ea9-49df-8844-79830adff1af)

##### Portfolio current weights

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/999b2938-6bba-4632-879f-517df64f3032)

##### Portfolio accumulation goals

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/3869c608-3b21-4e83-97b6-e681c43ec537)

##### Portfolio performance

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/a6da65a0-6ddb-4988-ad75-c91ff0e61e29)

As we can see, the largest profit comes from `ISAC`, followed by `VWCE`. We have too many **STOCKS**, too few **BONDS** and almost ideal amount of **GOLD**.

The current goal is to buy either 92 units of `VAGP` or 595 units of `SAGG` for **BONDS** and either 13 units of `4GLD` or 22 units of `IGLN`. I round the values ​​to the nearest whole number.

Our portfolio overall has 6.83% of profit. Which is 3339.49 euro.

#### Exemplary plot for portfolio profit over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/8feff9cd-f5f1-4465-9e55-7932cd7e3632)

The portfolio profit is positive almost all the time.

#### Exemplary plot for portfolio value and expenses over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/c382a4cd-34e9-4baa-9d95-e210e3022a4b)

#### Exemplary plot for portfolio drawdown over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/cd6f5595-a145-44f7-8a19-d8ae69b3721f)

We can see, that our portfolio had only one bigger drawdown in 2020.

#### Exemplary plot for a security value and expenses over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/94b976dd-6fef-44e0-93e9-acb94d8ca205)

#### Exemplary plot for a security profit over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/58967de0-0aac-461f-84ae-f8b16fdb26b5)

#### Exemplary plot for a security performance since its inception

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/fc006063-4eb0-456c-b6e1-53406ff4e9f8)
