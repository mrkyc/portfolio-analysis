# portfolio-analysis

Analysis and monitoring of the investment portfolio

## Overview

Based on the provided portfolio `.csv` files, the code calculates values such as securities value and profit over time. It converts all data to a specified **analysis currency** to facilitate the analysis.

Additionally, it generates analysis plots described below.

It is mainly intended for portfolios consisting of ETFs. Therefore, I will use ETFs in examples below.

### Console tables

Code prints four console tables:

1. Portfolio current status.

    The columns in the table represent each security held in the portfolio. Rows indicates:

    - **count** - Number of units of a given security.
    - **expense** - Sum of expenses for a specific security (without fees that can be specified in the dedicated column).
    - **value** - Current value of the corresponding security position.
    - **profit** - Current profit from that position.
    - **percentage profit** - Current percentage profit from the respective security position.

2. Portfolio current weights.
   
   Security weight groups in column. Rows indicates:

    - **share** - Current share in the portfolio.
    - **deviation from model weights** - The difference between model weights and current weights.
    - **ideal value** - The ideal (model) value.
    - **current value** - Sum of current values of securities in a given group.

3. Accumulation goals of the portfolio.
   
   This table is intended to facilitate the realization of a buy-and-hold strategy, emphasizing the intention to refrain from selling any securities. Instead, the objective is to acquire a specific count of securities to align with the model weights. The weight groups are represented as columns. Additionally, there is an extra column _SUM_ which tells what is the value of the portfolio currently, and what will be its value if we will reach the goal. The rows consist of:

    - **value** - Goal value of a group.
    - **current value** - Sum of current values of securities in a given group.
    - **count to buy** - The amount of units of a specific security to buy is determined in order to meet the goal weight group value. If there is more than one security name in a group, it indicates the units amount for each of them, and buying one of the corresponding amount of them will meet the goal.
    - **current count** - Current units amount of a given security.

4. Portfolio performance.
   
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
- **analysis_currency** - The currency in which the analysis will be performed.
- **tickers_and_currencies** - A dictionary where the keys are for securities tickers and the values are for currencies for the corresponding securities.
- **weights** - A dictionary conatining weight groups names as keys and the securities name list (tickers characters before the dot) as the corresponding values.
- **portfolio_data_files_paths_and_payments_columns** - A dictionary with paths to portfolio files as keys. The values are smaller dictionaries, each containing two key-value pairs. The first pair has the key *TRANSACTION_PAYMENT*, and the corresponding value is the column name in the portfolio file representing transaction payments (buy/sell) without broker fees. The second pair has the key *FEE_PAYMENT*, and the corresponding value is the column name in the portfolio file representing fees payment for transactions.
- **transaction_payments** - A dictionary with the columns from portfolio data files specified as *TRANSACTION_PAYMENT* as keys. The values are the corresponding currencies in which the amount is specified.
- **fee_payments** - A dictionary with the columns from portfolio data files specified as *FEE_PAYMENT* as keys. The values are the corresponding currencies in which the amount is specified.
- **first_transaction_date** - The date of the first transaction in portfolio.
- **start_date** - Start date of the analysis is used to shorten the period of analysis. It does not influence the values themselves, just drop the earlier dates before the output. Must be equal or older than the *first_transaction_date* date.
- **end_date** - End date of the analysis is used to shorten the period of analysis by ending on the specified date. The printed tables will show the portfolio's and its components' states for that date.
- **ohlc** - Which of the open, high, low or close from the downloaded data should be used in analysis
- **plots_folder_path** - The folder where the plots will be saved. It will be created if does not exist.

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
 - number 1: `VWCE.DE`, `4GLD.DE`. Additional fee 4 Euro per transaction.
 - number 2: `VAGP.L`, `SAGG.L`. Additional fee 3 Euro per transaction.
 - number 3: `ISAC.L`, `IGLN.L`. Additional fee 3 Euro per transaction.

Transaction data from each broker is stored in the following portfolio data files:
1. `portfolio_broker1.csv` - for broker number 1.
2. `portfolio_broker2.csv` - for broker number 2.
3. `portfolio_broker3.csv` - for broker number 3.

Some files have different column names for transaction payments and fees. In our case, it's just about showing that the code can work with them. Mainly it would be used if we had different transaction currencies. In our case, we use euros in each brokerage account.
Therefore we specify:
- transaction_payments to be:
  - `"transaction": "EUR"`,
  - `"transactions": "EUR"`,
  - `"trx_values": "EUR"`
- fee_payments:
    - `"trx_fee": "EUR"`,
    - `"fees": "EUR"`

Our portfolio has the following weight groups:
- **STOCKS** 50% consisting of: `VWCE.DE`, `ISAC.L`
- **BONDS** 30% consisting of: `VAGP.L`, `SAGG.L` 
- **GOLD** 20% consisting of: `4GLD.DE`, `IGLN.L`

The date of the first transaction was `2019-07-29`. The analysis will be carried out in the period from `2019-07-29` to `2023-11-25`. We will analyse close prices as they are usually the best for such analysis. The folder for plots will be named `portfolio plots`.

### Results

#### Tables:
![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/48a8694b-7c1a-43e4-8534-5dcd79d8f80e)
![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/6d5a8874-7416-4dcb-8681-e390c2b68ac4)
![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/77bfa98b-29f4-4295-a5d1-a7b0a0b46776)
![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/1595759f-38b9-402f-bdda-e1ced019df24)

As we can see, the largest profit comes from `ISAC`, followed by `VWCE`. We have too many **STOCKS**, too few **BONDS** and almost ideal amount of **GOLD**.

The current goal is to buy either 92 units of `VAGP` or 595 units of `SAGG` for **BONDS** and either 13 units of `4GLD` or 22 units of `IGLN`. I'm rounding the values.

Our portfolio overall has 6.83% of profit. Which is 3339.49 Euro.

#### Exemplary plot for portfolio profit over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/ae5c0ac5-5782-44be-bd5e-d72df545f229)

The portfolio profit is positive almost all the time.

#### Exemplary plot for portfolio value and expenses over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/c8a4c9ab-3e76-4d6e-948a-8bbd57a11cf6)

#### Exemplary plot for portfolio drawdown over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/bc1bbf43-0c6e-415e-b06d-e0c7459aeea5)

We can see, that our portfolio had only one bigger drawdown in 2020.

#### Exemplary plot for a security value and expenses over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/64ad1700-4b55-4d7f-8067-270392dc69fe)

#### Exemplary plot for a security profit over time

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/71b137ef-b7a3-4457-8eed-1989f0bfda12)

#### Exemplary plot for a security performance since its inception

![image](https://github.com/mrkyc/portfolio-analysis/assets/82812493/b552107c-5e90-4223-879d-077b4ff626b5)
